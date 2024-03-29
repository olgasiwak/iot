"""Moduł odpowiedzialny za zbieranie informacji publikowanych przez sensory na odpowiednich topicach w brokerze mosquitto i sterowanie na ich podstawie zapalaniem lamp.
Zebrane informacje przekazywane są do modułu data2metric odpowiedzialnego za agregację i archiwizację informacji z sieci.
"""
import json
import time
import pprint
import re
import threading

import config
import paho.mqtt.client as mqtt
from lamp import Lamp
from lamp import LampState
from data2metric import InfluxClient

STATES = {}
LOCK = threading.Lock()


class CollectorExecutor:
    """Moduł odpowiedzialny za zbieranie informacji z sensorów i sterowanie zapalaniem lamp
    """
    def __init__(self):
        self.client = mqtt.Client()

    def change_lamps_states(self, lamp):
        """Metoda podejmująca decyzję o zaświeceniu lub zgaszeniu lamp na podstawie informacji o stanie sensora

        :param lamp: Obiekt klasy Lamp() zawierający informację o nazwie topicu grupy lamp i pożądnym stanie (ON/OFF) danej grupy
        :type lamp: Lamp
        :return:
        :rtype:
        """
        if lamp.state == LampState.on:
            self.send_on_signal(lamp.name)
        elif lamp.state == LampState.off:
            self.send_off_signal(lamp.name)
        else:
            config.logging.debug("Wrong message format")

    def send_on_signal(self, lamp_name):
        """Metoda publikująca informację o konieczności zaświecenia danej grupy lamp, na topic odpowiadający danej grupie lamp

        :param lamp_name: Nazwa topicu z którego przyszła informacja o konieczności zmiany stanu lamp
        :type lamp_name: String
        :return:
        :rtype:
        """
        topic_name = self.prepare_topic_name(lamp_name)
        config.logging.debug(f'Send on signal to {topic_name}')
        self.client.publish(topic_name, LampState.on.value)

    def send_off_signal(self, lamp_name):
        """Metoda publikująca informację o konieczności zgaszenia danej grupy lamp, na topic odpowiadający danej grupie lamp

        :param lamp_name: Nazwa topicu z którego przyszła informacja o konieczności zmiany stanu lamp
        :type lamp_name: String
        :return:
        :rtype:
        """
        topic_name = self.prepare_topic_name(lamp_name)
        config.logging.debug(f'Send off signal to {topic_name}')
        self.client.publish(topic_name, LampState.off.value)

    def prepare_topic_name(self, lamp_name):
        """Metoda wyliczająca nazwę topicu do sterowania daną grupą lamp na podstawie nazwy topicu z którego przyszła informacja o stanie grupy sensorów

        :param lamp_name: Nazwa topicu z którego przyszła informacja o stanie grupy sensorów
        :type lamp_name: String
        :return:
        :rtype:
        """
        sensor_group_name = re.split("/", lamp_name)[-1]
        return config.TOPIC_EXECUTOR_SENSORS_REGEX + sensor_group_name

    def on_connect(self, client, userdata, flags, rc):
        """Metoda wywoływana, gdy broker odpowiada na nasze żądanie połaczenia

        :param client: Instancja klasy Client
        :type client: MQTT Client
        :param userdata: Prywatne dane użytkownika określone w Client() lub user_data_set()
        :type userdata:
        :param flags: Flagi odpowiedzi wysyłane przez brokera
        :type flags:
        :param rc: wynik połączenia 0: Połączenie pomyślne 1: Połączenie odrzucone - niewłaściwa wersja protokołu 2: Połączenie odrzucone - nieprawidłowy identyfikator klienta 3: Połączenie odrzucone - serwer niedostępny 4: Połączenie odrzucone - zła nazwa użytkownika lub hasło 5: Połączenie odrzucone - brak autoryzacji 6-255: Obecnie nieużywane.
        :type rc: int
        :return:
        :rtype:
        """
        config.logging.debug(f'Connected with result code {str(rc)}')
        self.client.subscribe(config.TOPIC_SENSORS_COLLECTOR_REGEX)

    def on_message(self, client, userdata, msg):
        """Wywoływana, gdy odebrano wiadomość na topic subskrybowany przez klienta

        :param client: Instancja klasy Client
        :type client:  MQTT Client
        :param userdata: Prywatne dane użytkownika określone w CLient() lub user_data_set()
        :type userdata:
        :param msg: Instancja MQTTMessage
        :type msg:
        :return:
        :rtype:
        """
        global LOCK
        LOCK.acquire()
        if msg.topic not in STATES:
            config.logging.debug(f'Adding new sensor group {msg.topic}')
            STATES[msg.topic] = msg.payload.decode(config.ENCODING)
        elif STATES[msg.topic] != msg.payload.decode(config.ENCODING):
            STATES[msg.topic] = msg.payload.decode(config.ENCODING)
            state = int(STATES[msg.topic])
            self.notify_executor(Lamp(msg.topic, LampState(state)))
        config.logging.debug(pprint.pprint(STATES))
        LOCK.release()

    def notify_executor(self, lamp):
        """Metoda wysyłająca informację do executora w celu przełączenia stanu lampy na podstawie informacji z czujników

        :param lamp: Obiekt klasy Lampy() z informacją o nazwie topicu na który publikuje dana grupa sensorów i stanie grupy sensorów (obecność lub brak ruchu)
        :type lamp: Lamp
        :return:
        :rtype:
        """
        config.logging.debug('executor notified')
        self.change_lamps_states(lamp)
        pass

    def notify_data_to_metric(self, states, polling_cycle):
        """Metoda wysyłająca informacje o stanie sensorów do modułu data2metric

        :param states: Stan sensorów (0/1)
        :type states: int
        :param polling_cycle: Okres czasu co jaki informacje o stanie sensorów powinny być zapisywane
        :type polling_cycle: int
        :return:
        :rtype:
        """
        global LOCK
        while True:
            if not len(states):
                continue
            config.logging.debug('data2metric notified')
            LOCK.acquire()
            Influx = InfluxClient(config.INFLUX_ORG,
                                        config.INFLUX_URL,
                                        config.INFLUX_BUCKET,
                                        config.INFLUX_TOKEN
                                        )

            Influx.write_to_database(
                    Influx.prepare_single_sensor_datapoints(STATES))
            Influx.write_to_database(
                    [Influx.prepare_active_lanterns_ratio_datapoint(STATES)])
            LOCK.release()
            time.sleep(polling_cycle)

    def start_listening_loop(self):
        """Główna metoda konfigurująca klienta Paho MQTT i rozpoczynająca nasłuch informacji od sensorów na odpowiednich topicach

        :return:
        :rtype:
        """
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(config.MQTT_ADDRESS, config.MQTT_PORT, config.MQTT_TIMEOUT)
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            with open(config.BACKUP_STATEFILE, 'w') as backup:
                backup.write(json.dumps(STATES))
            config.logging.debug('disconnected')


if __name__ == "__main__":
    module = CollectorExecutor()
    thread_main = threading.Thread(target=module.start_listening_loop)
    thread_data2metric = threading.Thread(target=module.notify_data_to_metric, args=(STATES, config.DATA2METRIC_POLLING_CYCLE,))

    thread_main.start()
    thread_data2metric.start()

    thread_main.join()
    thread_data2metric.join()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
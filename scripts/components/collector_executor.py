"""Provide several sample math calculations.

This module allows the user to make mathematical calculations.

The module contains the following functions:

- `add(a, b)` - Returns the sum of two numbers.
- `subtract(a, b)` - Returns the difference of two numbers.
- `multiply(a, b)` - Returns the product of two numbers.
- `divide(a, b)` - Returns the quotient of two numbers.
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
    """This module collect data from sensors and send commands to lamps

    """
    def __init__(self):
        self.client = mqtt.Client()

    def change_lamps_states(self, lamp):
        """Choose method for switching lamp on or off

        :param lamp: Lamp object with information about lamp group name and state
        :type lamp: Lamp
        :return:
        :rtype:
        """
        if lamp.state == LampState.on:
            self.send_on_signal(lamp.name)
        elif lamp.state == LampState.off:
            self.send_off_signal(lamp.name)
        else:
            config.logger.debug("Wrong message format")

    def send_on_signal(self, lamp_name):
        """Publish "on" command on topic

        :param lamp_name: name of the lamp group
        :type lamp_name: String
        :return:
        :rtype:
        """
        topic_name = self.prepare_topic_name(lamp_name)
        config.logger.debug(f'Send on signal to {topic_name}')
        self.client.publish(topic_name, LampState.on.value)

    def send_off_signal(self, lamp_name):
        """Publish "off" command on topic

        :param lamp_name: name of the lamp group
        :type lamp_name: String
        :return:
        :rtype:
        """
        topic_name = self.prepare_topic_name(lamp_name)
        config.logger.debug(f'Send off signal to {topic_name}')
        self.client.publish(topic_name, LampState.off.value)

    def prepare_topic_name(self, lamp_name):
        """Prepare topic name based information about lamp name

        :param lamp_name:
        :type lamp_name: String
        :return:
        :rtype:
        """
        sensor_group_name = re.split("/", lamp_name)[-1]
        return config.TOPIC_EXECUTOR_SENSORS_REGEX + sensor_group_name

    def on_connect(self, client, userdata, flags, rc):
        """Subscribe to the topic on which sensors publish data

        :param client: client use for connection with mosquitto broker
        :type client: MQTT Client
        :param userdata:
        :type userdata:
        :param flags:
        :type flags:
        :param rc: Connection code 1 - success, 0 - failure
        :type rc: int
        :return:
        :rtype:
        """
        config.logger.debug(f'Connected with result code {str(rc)}')
        self.client.subscribe(config.TOPIC_SENSORS_COLLECTOR_REGEX)

    def on_message(self, client, userdata, msg):
        """Method that is run when information is received on topic

        :param client:  client use for connection with mosquitto broker
        :type client:  MQTT Client
        :param userdata:
        :type userdata:
        :param msg:
        :type msg:
        :return:
        :rtype:
        """
        global LOCK
        LOCK.acquire()
        if msg.topic not in STATES:
            config.logger.debug(f'Adding new sensor group {msg.topic}')
            STATES[msg.topic] = msg.payload.decode(config.ENCODING)
        elif STATES[msg.topic] != msg.payload.decode(config.ENCODING):
            STATES[msg.topic] = msg.payload.decode(config.ENCODING)
            state = int(STATES[msg.topic])
            self.notify_executor(Lamp(msg.topic, LampState(state)))
        config.logger.debug(pprint.pprint(STATES))
        LOCK.release()

    def notify_executor(self, lamp):
        """Method that send information to executor in order to switch lamp state based on information from sensors

        :param lamp: Lamp object with information about lamp group name and state
        :type lamp: Lamp
        :return:
        :rtype:
        """
        config.logger.debug('executor notified')
        self.change_lamps_states(lamp)
        pass

    def notify_data_to_metric(self, states, polling_cycle):
        """Method that sends information to data2metric module

        :param states: State of the sensors
        :type states: int
        :param polling_cycle:
        :type polling_cycle:
        :return:
        :rtype:
        """
        global LOCK
        while True:
            if not len(states):
                continue
            config.logger.debug('data2metric notified')
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
        """Main method with mosquitto broker loop

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
            config.logger.debug('disconnected')


if __name__ == "__main__":
    module = CollectorExecutor()
    thread_main = threading.Thread(target=module.start_listening_loop)
    thread_data2metric = threading.Thread(target=module.notify_data_to_metric, args=(STATES, config.DATA2METRIC_POLLING_CYCLE,))

    thread_main.start()
    thread_data2metric.start()

    thread_main.join()
    thread_data2metric.join()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
import json
import pprint
import re
import threading

import config
import paho.mqtt.client as mqtt
from lamp import Lamp
from lamp import LampState
from data2metric import InfluxClient

STATES = {}


class Module:
    def __init__(self):
        self.client = mqtt.Client()

    def change_lamps_states(self, lamp):
        if lamp.state == LampState.on:
            self.send_on_signal(lamp.name)
        elif lamp.state == LampState.off:
            self.send_off_signal(lamp.name)
        else:
            config.logger.debug("Wrong message format")

    def send_on_signal(self, lamp_name):
        topic_name = self.prepare_topic_name(lamp_name)
        config.logger.debug(f'Send on signal to {topic_name}')
        self.client.publish(topic_name, LampState.on.value)

    def send_off_signal(self, lamp_name):
        topic_name = self.prepare_topic_name(lamp_name)
        config.logger.debug(f'Send off signal to {topic_name}')
        self.client.publish(topic_name, LampState.off.value)

    def prepare_topic_name(self, lamp_name):
        sensor_group_name = re.split("/", lamp_name)[-1]
        return config.TOPIC_EXECUTOR_SENSORS_REGEX + sensor_group_name

    def on_connect(self, client, userdata, flags, rc):
        config.logger.debug(f'Connected with result code {str(rc)}')
        self.client.subscribe(config.TOPIC_SENSORS_COLLECTOR_REGEX)

    def on_message(self, client, userdata, msg):
        if msg.topic not in STATES:
            config.logger.debug(f'Adding new sensor group {msg.topic}')
            STATES[msg.topic] = msg.payload.decode(config.ENCODING)
        elif STATES[msg.topic] != msg.payload.decode(config.ENCODING):
            STATES[msg.topic] = msg.payload.decode(config.ENCODING)
            state = int(STATES[msg.topic])
            self.notify_executor(Lamp(msg.topic, LampState(state)))
        self.notify_data_to_metric(STATES)
        config.logger.debug(pprint.pprint(STATES))

    def notify_executor(self, lamp):
        config.logger.debug('executor notified')
        self.change_lamps_states(lamp)
        pass

    def notify_data_to_metric(self, states):
        config.logger.debug('data2metric notified')
        Influx = InfluxClient(config.INFLUX_ORG,
                                    config.INFLUX_URL,
                                    config.INFLUX_BUCKET,
                                    config.INFLUX_TOKEN
                                    )

        Influx.write_to_database(
                Influx.prepare_single_sensor_datapoints(STATES))
        Influx.write_to_database(
                [Influx.prepare_active_lanterns_ratio_datapoint(STATES)])

    def main(self):
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
    module = Module()
    module.main()

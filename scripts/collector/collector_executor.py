from enum import Enum

import paho.mqtt.client as mqtt
import threading
import json
import pprint
import socket

MQTT_ADDRESS = socket.gethostbyname(socket.gethostname())
MQTT_PORT = 1883
MQTT_TIMEOUT = 60

ENCODING = 'utf-8'
STATES = {}
BACKUP_STATEFILE = 'states.backup'


class LampState(Enum):
    on = 1
    off = 0


class Lamp:
    def __init__(self, name: str, state: LampState) -> None:
        self.name = name
        self.state = state


def change_lamps_states(lamp):
    if lamp.state == LampState.on:
        send_on_signal(lamp.name)
    elif lamp.state == LampState.off:
        send_off_signal(lamp.name)
    else:
        print("Wrong message format")


def send_on_signal(lamp_name):
    print(f'Send on signal to {lamp_name}')
    client = mqtt.Client()
    client.connect(MQTT_ADDRESS, MQTT_PORT, MQTT_TIMEOUT)
    client.publish(lamp_name, LampState.on.value)


def send_off_signal(lamp_name):
    print(f'Send off signal to {lamp_name}')
    client = mqtt.Client()
    client.publish(lamp_name, LampState.off.value)


def on_connect(client, userdata, flags, rc):
    print(f'Connected with result code {str(rc)}')
    client.subscribe('sensors/+')


def on_message(client, userdata, msg):
    if msg.topic not in STATES:
        STATES[msg.topic] = msg.payload.decode(ENCODING)
    elif STATES[msg.topic] != msg.payload.decode(ENCODING):
        STATES[msg.topic] = msg.payload.decode(ENCODING)
        state = int(STATES[msg.topic])
        notify_executor(Lamp(msg.topic, LampState(state)))
    print(pprint.pprint(STATES))


def notify_executor(lamp):
    print('executor notified')
    change_lamps_states(lamp)
    pass


def notify_data_to_metric():
    print('data2metric notified')
    # call date2metric class there
    threading.Timer(5.0, notify_data_to_metric()).start()
    pass


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_ADDRESS, MQTT_PORT, MQTT_TIMEOUT)
    try:
        # notify_data_to_metric()
        client.loop_forever()
    except KeyboardInterrupt:
        with open(BACKUP_STATEFILE, 'w') as backup:
            backup.write(json.dumps(STATES))
        print('disconnected')


if __name__ == "__main__":
    main()

# TODO convert into object oriented program
# TODO prepare a mechanism for switching on entire sections of lamps
# TODO prepare a mechanism for storing previous state of sensors

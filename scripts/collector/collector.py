import paho.mqtt.client as mqtt
import threading
import time
import json
import pprint
import socket

MQTT_ADDRESS = socket.gethostbyname(socket.gethostname())
MQTT_PORT = 1883
MQTT_TIMEOUT = 60

ENCODING = 'utf-8'
STATES = {}
BACKUP_STATEFILE = 'states.backup'

def on_connect(client, userdata, flags, rc):
    print(f'Connected with result code {str(rc)}')
    client.subscribe('sensors/+')

def on_message(client, userdata, msg):
    if msg.topic not in STATES:
        STATES[msg.topic] = msg.payload.decode(ENCODING)
    elif STATES[msg.topic] != msg.payload.decode(ENCODING):
        STATES[msg.topic] = msg.payload.decode(ENCODING)
        notify_executor()
    print(pprint.pprint(STATES))

def notify_executor():
    print('executor notified')
    #call executor class there
    pass

def notify_data_to_metric():
    print('data2metric notified')
    #call date2metric class there
    threading.Timer(5.0, notify_data_to_metric()).start()
    pass

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_ADDRESS, MQTT_PORT, MQTT_TIMEOUT)
    try:
        #notify_data_to_metric()
        client.loop_forever()
    except KeyboardInterrupt:
        with open(BACKUP_STATEFILE, 'w') as backup:
            backup.write(json.dumps(STATES))
        print('disconnected')

if __name__ == "__main__":
    main()


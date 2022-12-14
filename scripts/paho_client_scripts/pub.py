import paho.mqtt.client as mqtt
import time

ENCODING = 'utf-8'
MQTT_TOPICS = [('test_topic1', 0), ('test_topic2', 0)]

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPICS)

def on_message(client, userdata, msg):
    print(msg.topic + " " + msg.payload.decode(ENCODING))

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("192.168.161.89", 1883, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()

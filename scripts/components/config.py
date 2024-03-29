import socket
import logging
import sys
import os

""" Plik zawierający parametry konfiguracyjne dla modułu collector_executor
"""
# This one is for baremetal
# MQTT_ADDRESS = socket.gethostbyname(socket.gethostname())
# This one is for dockerized version
# MQTT_ADDRESS = 172.17.0.2
MQTT_PORT = 1883
MQTT_TIMEOUT = 60

ENCODING = 'utf-8'
BACKUP_STATEFILE = 'states.backup'
TOPIC_SENSORS_COLLECTOR_REGEX = 'sensors_group/collector/+'
TOPIC_EXECUTOR_SENSORS_REGEX = 'executor/sensors_group/'

INFLUX_ORG = 'IoT'
INFLUX_URL = 'http://192.168.179.97:8086'
INFLUX_BUCKET = 'IoT'
INFLUX_TOKEN = os.environ.get("INFLUXDB_TOKEN")

DATA2METRIC_POLLING_CYCLE = 1


logging.basicConfig(filename="logs.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Collector and executor logs: \n")


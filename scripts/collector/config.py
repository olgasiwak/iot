import socket
import logging
import sys
import os

MQTT_ADDRESS = socket.gethostbyname(socket.gethostname())
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

logger = logging.getLogger(__name__)
streamHandler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.DEBUG)
logger.addHandler(streamHandler)

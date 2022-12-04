import sys
import sqlalchemy
import threading
import logging
import config
from sqlalchemy.orm import Session
import paho.mqtt.client as mqtt
import models
import json
from sqlalchemy import select
from abc import ABC, abstractclassmethod

logger = logging.getLogger(__name__)
streamHandler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.DEBUG)
logger.addHandler(streamHandler)


class Module(ABC):
    @abstractclassmethod
    async def run(self) -> None:
        pass


class Discoverer(Module):
    def __init__(self):
        logger.debug("Connecting to DB ...")
        try:
            db_engine = sqlalchemy.create_engine(config.POSTGRESQL_DB_URL)
            self.session = Session(bind=db_engine)
        except sqlalchemy.exc.OperationalError:  # type: ignore
            logger.error("Failed to connect to Postgres!")
            raise

        logger.debug("Connecting to Broker ...")
        try:
            self.client = mqtt.Client()
            self.client.on_connect = self.on_broker_connect
            self.client.on_message = self.on_broker_message
            self.client.connect(config.BROKER_HOST,
                                config.BROKER_PORT, keepalive=60)
        except ConnectionRefusedError:
            logger.error("Failed to connect to Broker!")

    def on_broker_connect(self, client, userdata, flags, rc):
        logger.debug(f'Connected to broker with result code {str(rc)}')
        self.client.subscribe(config.BROKER_DISCOVERY_TOPIC)

    def on_broker_message(self,
                          client: mqtt.Client,
                          userdata,
                          msg: mqtt.MQTTMessage) -> None:
        try:
            data = msg.payload.decode('utf-8')
        except json.JSONDecodeError:
            logger.error("Error while decoding client hello message")
            return

        client_data = json.loads(data)
        logger.debug(msg.topic+" "+data)
        p = threading.Thread(target=self.handle_hello_message,
                             args=(client_data,))
        p.start()

    def handle_hello_message(self, data: dict) -> None:
        udid = data["udid"]
        mac = data["mac"]
        with self.session as s:
            stmt = select(models.Devices) \
                .where(models.Devices.udid == udid) \
                .where(models.Devices.mac == mac)
            results = s.execute(stmt).all()

            # it's supposed to have either 1 or 0 elements as UDID is unique
            if results:
                logger.debug(f"Found device {results[0]}")
                # configre ACLs to allow access
                self.configure_allowing_acl()
            else:
                logger.info(
                    f"No devices found with MAC: {mac} and UDID: {udid}")
                # block the thing out
                self.configure_blocking_acl()

    def configure_blocking_acl(self):
        pass

    def configure_allowing_acl(self):
        pass

    def run(self):
        logger.debug("Listening...")
        self.client.loop_forever()


if __name__ == "__main__":
    mock = Discoverer()
    mock.run()

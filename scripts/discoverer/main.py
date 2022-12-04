import typing as t
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
            self.client = mqtt.Client(client_id="Discoverer")
            # self.client.enable_logger(logger)
            self.client.username_pw_set("discovery", "discovery")
            self.client.on_connect = self.on_broker_connect
            self.client.on_message = self.on_broker_message
            self.client.connect(config.BROKER_HOST,
                                config.BROKER_PORT, keepalive=60)
        except ConnectionRefusedError:
            logger.error("Failed to connect to Broker!")

        self.guard = Guardian()

    def create_roles_for_devices(self):
        with self.session as s:
            stmt = select(models.Devices).all()
            result = s.execute(stmt)
            for device in result:
                self.guard.create_role(
                    role_name=f"iot_{device.udid}",
                    topics_to_send=[f"collector/{device.udid}", ],
                    topics_to_subscribe=[f"discoverer/config/{device.udid}", ],
                    topics_to_receive=[f"discoverer/config/{device.udid}", ]
                )
                self.guard.create_client(
                    client_name=f"{device.udid}",
                    client_password=f"{device.udid}",
                    role_name=f"iot_{device.udid}"
                )

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
        logger.debug(msg.topic + " " + data)
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
            else:
                logger.info(
                    f"No devices found with MAC: {mac} and UDID: {udid}")

    def run(self):
        logger.debug("Listening...")
        self.client.loop_forever()


class Guardian(Module):
    def __init__(self):
        self.client = mqtt.Client(client_id="Guardian")
        # self.client.enable_logger(logger)
        self.admin_topic = config.BROKER_DYNAMIC_SECURITY_TOPIC
        self.client.username_pw_set(config.BROKER_ADMIN_LOGIN,
                                    config.BROKER_ADMIN_PASSWORD)
        self.client.connect(config.BROKER_HOST,
                            config.BROKER_PORT, keepalive=60)

    def create_role(self, role_name: str,
                    topics_to_send: t.Sequence[str] = [],
                    topics_to_subscribe:  t.Sequence[str] = [],
                    topics_to_receive:  t.Sequence[str] = []):
        message = {
            "commands": [
                {
                    "command": "modifyRole",
                    "rolename": role_name,
                    "acls":
                        [{"acltype": "publishClientSend",
                          "topic": topic_to_send,
                          "allow": True}
                         for topic_to_send in topics_to_send] +
                        [{"acltype": "subscribeLiteral",
                          "topic": topic_to_subscribe, "allow": True}
                         for topic_to_subscribe in topics_to_subscribe] +
                        [{"acltype": "publishClientReceive",
                          "topic": topic_to_receive, "allow": True}
                         for topic_to_receive in topics_to_receive]
                }
            ]
        }
        self.client.publish(self.admin_topic, json.dumps(message))

    def create_default_config(self):
        message = {
            "commands": [
                {
                    "command": "setDefaultACLAccess",
                    "acls": [
                        {"acltype": "publishClientSend", "allow": False},
                        {"acltype": "publishClientReceive", "allow": False},
                        {"acltype": "subscribe", "allow": False},
                        {"acltype": "unsubscribe", "allow": False}
                    ]
                }
            ]
        }
        self.client.publish(self.admin_topic, json.dumps(message))

    def create_client(self, client_name: str,
                      client_password: str, role_name: str):
        message = {
            "commands": [
                {
                    "command": "createClient",
                    "username": client_name,
                    "password": client_password,
                    "roles": [
                        {"rolename": role_name, "priority": -1}
                    ]
                }
            ]
        }
        self.client.publish(self.admin_topic, json.dumps(message))

    def create_anonymous_group(self):
        message = {
            "commands": [
                {
                    "command": "createGroup",
                    "groupname": "anonymous",
                    "roles": [
                        {"rolename": "default_restricted"}
                    ]

                }
            ]
        }
        self.client.publish(self.admin_topic, json.dumps(message))
        message = {
            "commands": [
                {
                    "command": "setAnonymousGroup",
                    "groupname": "anonymous"
                }
            ]
        }
        self.client.publish(self.admin_topic, json.dumps(message))

    def create_default_clients(self) -> None:
        self.create_client(
            client_name="discovery",
            client_password="discovery",
            role_name="discoverer"
        )

    def create_default_roles(self) -> None:
        self.create_role(
            role_name="default_restricted",
            topics_to_send=[config.BROKER_DISCOVERY_TOPIC, ],
        )

        self.create_role(
            role_name="discoverer",
            topics_to_send=[config.BROKER_CONFIGURATION_TOPIC, ],
            topics_to_subscribe=[config.BROKER_DISCOVERY_TOPIC, ],
            topics_to_receive=[config.BROKER_DISCOVERY_TOPIC, ]
        )

    def run(self):
        self.create_default_config()
        self.create_default_roles()
        self.create_anonymous_group()
        self.create_default_clients()


if __name__ == "__main__":
    disc = Discoverer()
    disc.run()

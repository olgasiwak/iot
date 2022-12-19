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
    def run(self) -> None:
        pass


class Discoverer(Module):
    """Discoverer module class"""

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
        self.guard.run()

    def send_configuration(self, device: models.Devices):
        """
        Publishes a JSON with configuration to the config topic 
        of a given device.
        """
        logger.debug(f"Sending config to {device}...")
        payload: dict = device.group.configuration

        self.client.publish(
            topic=config.BROKER_CONFIGURATION_TOPIC.format(udid=device.udid),
            payload=json.dumps(payload).encode("utf-8")
        )

    def on_broker_connect(self, client, userdata, flags, rc):
        """
        Handler function that runs after Discoverer establishes connetction to 
        the broker.
        """
        logger.debug(f'Connected to broker with result code {str(rc)}')
        self.client.subscribe(config.BROKER_DISCOVERY_TOPIC)
        with self.session as s:
            stmt = select(models.Devices)
            result = s.execute(stmt).all()
            self.guard.create_roles_for_devices(result)

    def on_broker_message(self,
                          client: mqtt.Client,
                          userdata,
                          msg: mqtt.MQTTMessage) -> None:
        """
        Handler function that takes care of new messages from the subscribed 
        topics.
        """
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
        """
        Identifies devices based on the provided data by quering AssetDB.
        """
        udid = data["udid"]
        mac = data["mac"]
        with self.session as s:
            stmt = select(models.Devices) \
                .where(models.Devices.udid == udid) \
                .where(models.Devices.mac == mac)
            results = s.execute(stmt).all()

            # it's supposed to have either 1 or 0 elements as UDID is unique
            if results:
                res: models.Devices = results[0][0]
                logger.debug(f"Found device {res}")
                self.send_configuration(res)
            else:
                logger.info(
                    f"No devices found with MAC: {mac} and UDID: {udid}")

    def run(self):
        logger.debug("Listening...")
        self.client.loop_forever()


class Guardian(Module):
    """Guardian module class

    It authorizes using admin passes and publishes on special config topic
    for dynamic security plugin.
    """

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
        """
        Creates a new role with provided name and ACLs per topic.
        """
        message = {
            "commands": [
                {
                    "command": "createRole",
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
        """
        Configures default broker ACLs with zero trust policy.
        """
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
        """
        Creates a dynamic security client with a given name,
        password and assigns to the specified role.
        """
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
        """
        Not used.
        Creates an anonymous group to which each unidentified client is assigned.
        """
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

    def create_roles_for_devices(self, devices: t.Sequence[models.Devices]):
        """
        Creates ACLs for the provided devices.
        """
        for _device in devices:
            device = _device[0]
            self.create_role(
                role_name=f"iot_{device.udid}",
                topics_to_send=[f"collector/{device.udid}",
                                config.BROKER_DISCOVERY_TOPIC],
                topics_to_subscribe=[f"discoverer/config/{device.udid}", ],
                topics_to_receive=[f"discoverer/config/{device.udid}", ]
            )
            self.create_client(
                client_name=f"{device.udid}",
                client_password=f"{device.udid}",
                role_name=f"iot_{device.udid}"
            )

    def create_default_clients(self) -> None:
        """
        Creates default dynamic security clients.
        """
        self.create_client(
            client_name="discovery",
            client_password="discovery",
            role_name="discoverer"
        )

    def create_default_roles(self) -> None:
        """
        Creates default roles.
        """
        self.create_role(
            role_name="default_restricted",
            topics_to_send=[config.BROKER_DISCOVERY_TOPIC, ],
        )

        self.create_role(
            role_name="discoverer",
            topics_to_send=["discovery/config/#", ],
            topics_to_subscribe=[config.BROKER_DISCOVERY_TOPIC, ],
            topics_to_receive=[config.BROKER_DISCOVERY_TOPIC, ]
        )

    def run(self):
        self.create_default_config()
        self.create_default_roles()
        self.create_default_clients()


if __name__ == "__main__":
    disc = Discoverer()
    disc.run()

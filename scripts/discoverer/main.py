import sys
import sqlalchemy
import asyncio
import logging
import config
from sqlalchemy.orm import Session
import paho.mqtt.client as mqtt
import models

from abc import ABC, abstractclassmethod

logger = logging.getLogger(__name__)
streamHandler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.DEBUG)
logger.addHandler(streamHandler)


class Module(ABC):
    @abstractclassmethod
    async def on_start(self) -> None:
        pass


class Discoverer(Module):
    async def on_start(self) -> None:
        """This fucntions is responsible for module warm up."""
        logger.debug("Verifying connection to DB ...")
        try:
            db_engine = sqlalchemy.create_engine(config.POSTGRESQL_DB_URL)
            with Session(db_engine) as session:
                session.flush()
        except sqlalchemy.exc.OperationalError:
            logger.error("Failed to connect to Postgres!")
            raise

        logger.debug("Verifying connection to Broker ...")
        try:
            client = mqtt.Client()
            client.connect(config.BROKER_HOST, config.BROKER_PORT, keepalive=60)
        except ConnectionRefusedError:
            logger.error("Failed to connect to Broker!")
            raise


if __name__ == "__main__":
    mock = Discoverer()
    asyncio.run(mock.on_start())

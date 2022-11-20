import sys
import sqlalchemy
import asyncio
import logging
import config
import psycopg2

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

        # verify connection to DB
        logger.debug("Verifying connection to DB ...")
        try:
            db_engine = sqlalchemy.create_engine(config.POSTGRESQL_DB_URL)
            print(db_engine.connect())
        except psycopg2.OperationalError:
            logger.error("Failed to connect to Postgres!")
        # verify connection to Broker
        logger.debug("Verifying connection to Broker ...")
        pass


if __name__ == "__main__":
    mock = Discoverer()
    asyncio.run(mock.on_start())

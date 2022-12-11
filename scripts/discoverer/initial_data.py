import sqlalchemy
import config
from sqlalchemy.orm import Session
import models


def initialize_db():
    engine = sqlalchemy.create_engine(config.POSTGRESQL_DB_URL)
    with Session(engine) as session:
        version = models.Versions(id=1, hw_type="v0.1",
                                  description="version uno")
        client = models.Clients(id=1, name="Park Jordana",
                                description="To ten taki duzy")
        group = models.Groups(id=1, client=client, quantity=5,
                              description="To tam w parku",
                              configuration={"lower_threshold": 0.2,
                                             "upper_threshold": 0.85})
        device_1 = models.Devices(
            id=1,
            udid="agh-123456",
            mac="AB:CD:EF",
            longitude="12.123123",
            latitude="12.123123",
            version=version,
            group=group
        )
        device_2 = models.Devices(
            id=2,
            udid="agh-654321",
            mac="12:34:56",
            longitude="65.123123",
            latitude="55.123123",
            version=version,
            group=group
        )

        session.add_all([version, client, group, device_1, device_2])
        session.commit()


if __name__ == "__main__":
    initialize_db()

BROKER_HOST = "localhost"
BROKER_PORT = 1883

POSTGRESQL_DB_HOST = "0.0.0.0"
POSTGRESQL_DB_PORT = 5432
POSTGRESQL_DB_NAME = "main"
POSTGRESQL_DB_USERNAME = "postgres"
POSTGRESQL_DB_PASSWORD = "admin"
POSTGRESQL_DB_URL = f"postgresql+psycopg2://{POSTGRESQL_DB_USERNAME}:" + \
                    f"{POSTGRESQL_DB_PASSWORD}@" + \
                    f"{POSTGRESQL_DB_HOST}/{POSTGRESQL_DB_NAME}"
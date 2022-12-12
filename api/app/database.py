from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Baremetal
#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@127.0.0.1/start_listening_loop"
# Docker container
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@172.17.0.2/start_listening_loop"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


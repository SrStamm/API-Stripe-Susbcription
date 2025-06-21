from sqlalchemy import engine
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text
from models import plan, user, subscription
from dotenv import load_dotenv
import os

load_dotenv()

url = os.environ.get("DATABASE_URL")

engine = create_engine(url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"Conectado a PostgreSQL: {result.fetchone()}")
    except Exception as e:
        raise Exception(f"Error al conectar a la base de datos: {e}")


def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

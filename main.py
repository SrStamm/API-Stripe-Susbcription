from fastapi import FastAPI
from db.session import create_db_and_tables
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {
        "detail": "Bienvenido a stripe-fastapi! Una API conectada a stripe que permite manejar suscripciones."
    }


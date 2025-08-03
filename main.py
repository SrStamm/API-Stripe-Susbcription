from fastapi import FastAPI
from db.session import create_db_and_tables
from contextlib import asynccontextmanager
from api import users, subscriptions, plans, auth, webhooks, products


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(subscriptions.router)
app.include_router(auth.router)
app.include_router(plans.router)
app.include_router(webhooks.router)
app.include_router(products.router)


@app.get("/")
def root():
    return {
        "detail": "Bienvenido a stripe-fastapi! Una API conectada a stripe que permite manejar suscripciones."
    }

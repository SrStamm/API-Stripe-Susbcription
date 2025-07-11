from db.session import get_session
from repositories.user_repositories import UserRepository
from core.logger import logger
from tasks.app import app


@app.task
def customer_created(payload: dict):
    session = next(get_session())
    user_repo = UserRepository(session)

    user = user_repo.get_user_by_customer_id(payload["id"])

    if not user:
        user = user_repo.create(email=payload["email"])

        user_repo.update(id=user.id, stripe_id=payload["id"])


@app.task
def customer_deleted(payload: dict):
    session = next(get_session())
    user_repo = UserRepository(session)

    try:
        logger.info("Customer ID es: ", payload["id"])
        user_repo.delete(payload["id"])
    except Exception as e:
        raise e

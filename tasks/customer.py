from db.session import get_session
from repositories.user_repositories import UserRepository
from core.logger import logger
from schemas.exceptions import DatabaseError
from tasks.app import app


@app.task(
    bind=True,
    autoretry_for=(
        Exception,
        DatabaseError,
    ),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def customer_created(payload: dict):
    session = next(get_session())
    user_repo = UserRepository(session)

    try:
        user = user_repo.get_user_by_customer_id(payload["id"])

        if not user:
            user = user_repo.create(email=payload["email"])

            user_repo.update(id=user.id, stripe_id=payload["id"])

    except DatabaseError as e:
        logger.error(f"Database error in customer_created for {payload['id']}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in customer_created for {payload['id']}: {e}")
        raise


@app.task(
    bind=True,
    autoretry_for=(
        Exception,
        DatabaseError,
    ),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def customer_deleted(payload: dict):
    session = next(get_session())
    user_repo = UserRepository(session)

    try:
        logger.info("Customer ID es: ", payload["id"])
        user_repo.delete(payload["id"])

    except DatabaseError as e:
        logger.error(f"Database error in customer_deleted for {payload['id']}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in customer_deleted for {payload['id']}: {e}")
        raise

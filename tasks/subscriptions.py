from db.session import get_session
from repositories.subscription_repositories import SubscriptionRepository
from core.logger import logger
from datetime import datetime
from tasks.app import app
from schemas.exceptions import DatabaseError


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
def customer_subscription_created(payload: dict):
    session = next(get_session())
    subs_repo = SubscriptionRepository(session)

    try:
        logger.info(f"Customer.Subscription.created: {payload}")

        current_period_end = datetime.fromtimestamp(
            payload["items"]["data"][0]["current_period_end"]
        )

        subs_repo.update_for_user(
            sub_id=payload["id"],
            customer_id=payload["customer"],
            status=payload["status"],
            current_period_end=current_period_end,
            is_active=True,
        )
        logger.info(f"Customer subscription {payload['id']} updated correctly")

    except DatabaseError as e:
        logger.error(
            f"Database error in customer_subscription_created for {payload['id']}: {e}"
        )
        raise
    except Exception as e:
        logger.error(f"Error in Customer Subscription Created: {e}")
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
def customer_subscription_updated(payload: dict):
    session = next(get_session())
    subs_repo = SubscriptionRepository(session)

    try:
        # Obtiene el periodo de finalización de la suscripcion
        current_period_end = datetime.fromtimestamp(
            payload["items"]["data"][0]["current_period_end"]
        )

        subs_repo.update_for_user(
            sub_id=payload["id"],
            customer_id=payload["customer"],
            status=payload["status"],
            current_period_end=current_period_end,
            is_active=True,
        )

        logger.info(f"Customer subscription {payload['id']} updated correctly")

    except DatabaseError as e:
        logger.error(
            f"Database error in customer_subscription_updated for {payload['id']}: {e}"
        )
        raise
    except Exception as e:
        logger.error(f"Error in Customer Subscription Updated: {e}")
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
def customer_subscription_deleted(payload: dict):
    session = next(get_session())
    subs_repo = SubscriptionRepository(session)

    try:
        current_period_end = datetime.fromtimestamp(
            payload["items"]["data"][0]["current_period_end"]
        )

        subs_repo.cancel(
            sub_id=payload["id"],
            customer_id=payload["customer"],
            status=payload["status"],
            current_period_end=current_period_end,
        )
        logger.info(f"Customer subscription {payload['id']} updated correctly")

    except DatabaseError as e:
        logger.error(
            f"Database error in customer_subscription_deleted for {payload['id']}: {e}"
        )
        raise
    except Exception as e:
        logger.error(f"Error in Customer Subscription Deleted: {e}")
        raise

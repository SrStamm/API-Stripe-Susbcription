from db.session import get_session
from repositories.subscription_repositories import SubscriptionRepository
from core.logger import logger
from datetime import datetime
from tasks.app import app


@app.task
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

    except Exception as e:
        logger.error(f"Error in Customer Subscription Created: {e}")
        raise Exception("Internal Server Error")


@app.task
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

    except Exception as e:
        logger.error(f"Error in Customer Subscription Updated: {e}")
        raise Exception("Internal Server Error")


@app.task
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

    except Exception as e:
        logger.error(f"Error in Customer Subscription Deleted: {e}")
        raise Exception("Internal Server Error")

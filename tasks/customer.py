from fastapi import HTTPException
from db.session import get_session
from repositories.subscription_repositories import SubscriptionRepository
from repositories.user_repositories import UserRepository
from core.logger import logger
from datetime import datetime
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
def customer_subscription_created(payload: dict):
    session = next(get_session())
    subs_repo = SubscriptionRepository(session)

    try:
        logger.info(f"Customer.Subscription.created: {payload}")

        # Obtiene info de metadata
        metadata = payload.get("metadata")
        plan_id = metadata["plan_id"]
        user_id = metadata["user_id"]

        logger.info(f"plan_id: {plan_id}, user_id: {user_id}")

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
        raise HTTPException(500, detail="Internal Server Error")


@app.task
def customer_subscription_updated(payload: dict):
    session = next(get_session())
    subs_repo = SubscriptionRepository(session)

    try:
        logger.info(f"Customer.Subscription.updated: {payload}")

        # Obtiene info de metadata
        metadata = payload.get("metadata")
        plan_id = metadata["plan_id"]
        user_id = metadata["user_id"]

        logger.info(f"plan_id: {plan_id}, user_id: {user_id}")

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
        raise HTTPException(500, detail="Internal Server Error")


@app.task
def customer_subscription_deleted(payload: dict):
    session = next(get_session())
    subs_repo = SubscriptionRepository(session)

    try:
        logger.info(f"Customer.Subscription.deleted: {payload}")

        # Obtiene info de metadata
        metadata = payload.get("metadata")
        user_id = metadata["user_id"]

        logger.info(f"user_id: {user_id}")

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
        raise HTTPException(500, detail="Internal Server Error")

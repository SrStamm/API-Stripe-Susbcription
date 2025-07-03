from fastapi import HTTPException
from db.session import get_session
from repositories.subscription_repositories import SubscriptionRepository
from repositories.user_repositories import UserRepository
from core.logger import logger
from datetime import datetime


def customer_created(payload: dict):
    session = next(get_session())
    user_repo = UserRepository(session)

    user = user_repo.get_user_by_customer_id(payload["id"])

    if not user:
        user = user_repo.create(email=payload["email"])

        user_repo.update(id=user.id, stripe_id=payload["id"])


def invoice_paid(payload: dict):
    session = next(get_session())
    subs_repo = SubscriptionRepository(session)

    try:
        logger.info(f"Webhook payload: {payload}")

        # Ignorar facturas no relacionadas a suscripciones
        if payload.get("billing_reason") != "subscription_create":
            logger.info("Skipping invoice.paid: not from subscription")
            return

        lines = payload.get("lines", {}).get("data", [])
        if not lines:
            logger.warning("No invoice lines found in webhook payload")
            raise HTTPException(400, detail="Missing invoice lines")

        line = lines[0]

        parent = line.get("parent", {})

        sub_item_details = parent.get("subscription_item_details")

        if not sub_item_details or not sub_item_details.get("subscription"):
            logger.warning("No subscription ID found in subscription_item_details")
            raise HTTPException(400, detail="Missing subscription ID")

        subscription_id = sub_item_details.get("subscription")

        if not subscription_id:
            logger.warning("Missing subscription ID in invoice line")
            raise HTTPException(400, detail="Missing subscription ID")

        customer_id = payload.get("customer")
        current_period_end = datetime.fromtimestamp(line["period"]["end"])
        status = payload.get("status")

        logger.info(
            f"Webhook invoice.paid - sub_id: {subscription_id}, customer_id: {customer_id}"
        )

        sub = subs_repo.get_subscription_for_user(
            sub_id=subscription_id, customer_id=customer_id
        )

        if not sub:
            raise HTTPException(404, detail="Subscription not found")

        subs_repo.update_for_user(
            sub_id=subscription_id,
            customer_id=customer_id,
            status=status,
            current_period_end=current_period_end,
            is_active=True,
        )

        logger.info(f"Subscription {subscription_id} updated correctly")

    except Exception as e:
        logger.error(f"Error in Invoice Paid: {e}")
        raise HTTPException(500, detail="Internal Server Error")


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

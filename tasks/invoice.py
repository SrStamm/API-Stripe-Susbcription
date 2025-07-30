from db.session import get_session
from repositories.subscription_repositories import SubscriptionRepository
from core.logger import logger
from datetime import datetime
from tasks.app import celery_app


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def invoice_paid(self, payload: dict):
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
            raise Exception("Missing invoice lines")

        line = lines[0]

        parent = line.get("parent", {})

        sub_item_details = parent.get("subscription_item_details")

        if not sub_item_details or not sub_item_details.get("subscription"):
            logger.warning("No subscription ID found in subscription_item_details")
            raise Exception("Missing subscription ID")

        subscription_id = sub_item_details.get("subscription")

        if not subscription_id:
            logger.warning("Missing subscription ID in invoice line")
            raise Exception("Missing subscription ID")

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
            raise Exception("Subscription not found")

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
        raise Exception("Internal Server Error")

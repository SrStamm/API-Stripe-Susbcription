from logging import log
from fastapi import HTTPException
from tasks.customer import (
    customer_created,
    customer_deleted,
)
from tasks.subscriptions import (
    customer_subscription_created,
    customer_subscription_deleted,
    customer_subscription_updated,
    customer_sub_basic,
)
from tasks.invoice import invoice_paid, invoice_payment_failed
from core.logger import logger


class WebhooksHandlerService:
    def handle(self, event: dict):
        try:
            type = event["type"]
            payload = event["data"]["object"]

            match type:
                case "invoice.paid":
                    invoice_paid.delay(payload)
                case "invoice.payment_failed":
                    invoice_payment_failed.delay(payload)

                case "customer.created":
                    customer_created.delay(payload)
                    customer_sub_basic.delay(payload)
                case "customer.deleted":
                    customer_deleted.delay(payload)

                case "customer.subscription.created":
                    customer_subscription_created.delay(payload)
                case "customer.subscription.updated":
                    customer_subscription_updated.delay(payload)
                case "customer.subscription.paused":
                    customer_subscription_updated.delay(payload)
                case "customer.subscription.deleted":
                    customer_subscription_deleted.delay(payload)

        except KeyError as e:
            logger.warning(f"Invalid event structure: {e}")
            raise HTTPException(400, detail="Invalid event payload")

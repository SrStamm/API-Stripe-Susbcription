from fastapi import HTTPException
from tasks.customer import (
    customer_created,
    customer_deleted,
)
from tasks.subscriptions import (
    customer_subscription_created,
    customer_subscription_deleted,
    customer_subscription_updated,
)
from tasks.invoice import invoice_paid
from core.logger import logger


class WebhooksHandlerService:
    def handle(self, event: dict):
        type = event["type"]
        payload = event["data"]["object"]

        if not type or not payload:
            logger.warning("Invalid event structure")
            raise HTTPException(400, detail="Invalid event payload")

        match type:
            case "invoice.paid":
                invoice_paid.delay(payload)
            case "customer.created":
                customer_created.delay(payload)
            case "customer.deleted":
                customer_deleted.delay(payload)
            case "customer.subscription.created":
                customer_subscription_created.delay(payload)
            case "customer.subscription.updated":
                customer_subscription_updated.delay(payload)
            case "customer.subscription.deleted":
                customer_subscription_deleted.delay(payload)

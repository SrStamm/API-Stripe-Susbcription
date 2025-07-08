from tasks.customer import (
    customer_created,
    customer_subscription_created,
    customer_subscription_deleted,
    customer_subscription_updated,
)
from tasks.invoice import invoice_paid


class WebhooksHandlerService:
    def handle(self, event: dict):
        # Obtiene el tipo de evento y la información
        type = event["type"]
        payload = event["data"]["object"]

        match type:
            case "invoice.paid":
                invoice_paid.delay(event["data"]["object"])
            case "customer.created":
                customer_created.delay(payload)
            case "customer.subscription.created":
                customer_subscription_created.delay(payload)
            case "customer.subscription.updated":
                customer_subscription_updated.delay(payload)
            case "customer.subscription.deleted":
                customer_subscription_deleted.delay(payload)

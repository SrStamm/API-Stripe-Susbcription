from tasks import (
    invoice_paid,
    customer_created,
    customer_subscription_created,
    customer_subscription_updated,
    customer_subscription_deleted,
)


class WebhooksHandlerService:
    def handle(self, event: dict):
        # Obtiene el tipo de evento y la información
        type = event["type"]
        payload = event["data"]["object"]

        match type:
            case "invoice.paid":
                invoice_paid(payload)
            case "customer.created":
                customer_created(payload)
            case "customer.subscription.created":
                customer_subscription_created(payload)
            case "customer.subscription.updated":
                customer_subscription_updated(payload)
            case "customer.subscription.deleted":
                customer_subscription_deleted(payload)

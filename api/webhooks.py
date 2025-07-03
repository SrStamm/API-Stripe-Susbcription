from fastapi import APIRouter, HTTPException, Request
from core.logger import logger
from core.stripe_test import parse_webhook_event
from tasks import invoice_paid

router = APIRouter()


@router.post("/webhooks/")
async def handle_webhooks(request: Request):
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(400, detail="Stripe-Signature header missing")

    try:
        body = await request.body()
        event = parse_webhook_event(body, sig_header)

        logger.info(f"Received webhook event: {event['type']}")

        payload = event["data"]["object"]

        if event["type"] == "invoice.paid":
            invoice_paid(payload)

        elif event["type"] == "customer.created":
            print(f"Customer created: {payload['id']}")

        return {"status": "success"}

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(500, detail=f"Webhook processing error: {e}")

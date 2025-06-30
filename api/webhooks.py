from fastapi import APIRouter, HTTPException, Request
from core.logger import logger
from core.stripe_test import parse_webhook_event

router = APIRouter()


@router.post("/webhooks/")
async def handle_webhooks(request: Request):
    payload = await request.body()
    logger.info(f"payload: {payload}")

    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(400, detail="Stripe-Signature header missing")

    try:
        event = parse_webhook_event(payload, sig_header)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(500, detail=f"Webhook processing error: {e}")

    logger.info(f"Received webhook event: {event['type']}")

    if event["type"] == "customer.created":
        customer = event["data"]["object"]
        print(f"Customer created: {customer['id']}")

    return {"status": "success"}

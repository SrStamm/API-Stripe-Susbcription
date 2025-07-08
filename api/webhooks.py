from fastapi import APIRouter, HTTPException, Request
from core.logger import logger
from core.stripe_test import parse_webhook_event
from services.webhook_handler_service import WebhooksHandlerService

router = APIRouter()


@router.post("/webhooks/")
async def handle_webhooks(request: Request):
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(400, detail="Stripe-Signature header missing")

    try:
        # Obtiene el request
        body = await request.body()

        # Parsea el evento
        event = parse_webhook_event(body, sig_header)

        # Interactua el service con el evento
        handler = WebhooksHandlerService()
        handler.handle(event)

        return {"status": "success"}

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(500, detail=f"Webhook processing error: {e}")

from pydantic import ValidationError

from core.logger import logger
from parsers.invoice import (
    InvoicePayload,
    parse_invoice_paid,
    parse_invoice_payment_failed,
)
from helpers.context import get_subscription_service
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
    """Handle invoice.paid webhook."""
    # Validate payload structure
    try:
        data = InvoicePayload(**payload)
    except ValidationError as e:
        logger.warning(f"Invalid invoice.paid payload: {e}")
        return  # No retry for validation errors

    # Parse to extract needed info
    info = parse_invoice_paid(data)

    # Skip if invoice is not related to subscriptions
    if info is None:
        return

    # Execute service
    with get_subscription_service() as service:
        service.handle_invoice_paid(info)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def invoice_payment_failed(self, payload: dict):
    """Handle invoice.payment_failed webhook."""
    # Validate payload structure
    try:
        data = InvoicePayload(**payload)
    except ValidationError as e:
        logger.warning(f"Invalid invoice.payment_failed payload: {e}")
        return  # No retry for validation errors

    # Parse to extract needed info
    info = parse_invoice_payment_failed(data)

    # Execute service
    with get_subscription_service() as service:
        service.handle_invoice_payment_failed(info)
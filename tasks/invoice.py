from typing import Optional

from pydantic import ValidationError

from core.logger import logger
from core.correlation import set_correlation_id, clear_correlation_id
from parsers.invoice import (
    InvoicePayload,
    parse_invoice_paid,
    parse_invoice_payment_failed,
)
from helpers.context import get_subscription_service
from tasks.app import celery_app


def _setup_correlation_context(correlation_id: Optional[str] = None):
    """Setup correlation ID context for logging."""
    if correlation_id:
        set_correlation_id(correlation_id)


def _cleanup_correlation_context():
    """Cleanup correlation ID context."""
    clear_correlation_id()


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def invoice_paid(self, payload: dict, correlation_id: Optional[str] = None):
    """Handle invoice.paid webhook."""
    _setup_correlation_context(correlation_id)
    try:
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
    finally:
        _cleanup_correlation_context()


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def invoice_payment_failed(self, payload: dict, correlation_id: Optional[str] = None):
    """Handle invoice.payment_failed webhook."""
    _setup_correlation_context(correlation_id)
    try:
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
    finally:
        _cleanup_correlation_context()
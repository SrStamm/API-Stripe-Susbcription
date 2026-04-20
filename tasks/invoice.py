from db.session import get_session
from repositories.subscription_repositories import SubscriptionRepository
from services.subscription_service import SubscriptionService
from parsers.invoice import (
    InvoicePayload,
    parse_invoice_paid,
    parse_invoice_payment_failed,
)
from tasks.app import celery_app


def _get_subscription_service() -> SubscriptionService:
    """Create SubscriptionService instance for Celery tasks."""
    session = next(get_session())
    subs_repo = SubscriptionRepository(session)
    return SubscriptionService(subs_repo, None, None)


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
    data = InvoicePayload(**payload)

    # Parse to extract needed info
    info = parse_invoice_paid(data)

    # Skip if invoice is not related to subscriptions
    if info is None:
        return

    # Execute service
    service = _get_subscription_service()
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
    data = InvoicePayload(**payload)

    # Parse to extract needed info
    info = parse_invoice_payment_failed(data)

    # Execute service
    service = _get_subscription_service()
    service.handle_invoice_payment_failed(info)
from pydantic import ValidationError

from core.logger import logger
from parsers.customer import (
    CustomerPayload,
    parse_customer_created,
    parse_customer_deleted,
)
from helpers.context import get_customer_service
from tasks.app import celery_app


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def customer_created(self, payload: dict):
    """Handle customer.created webhook."""
    # Validate payload structure
    try:
        data = CustomerPayload(**payload)
    except ValidationError as e:
        logger.warning(f"Invalid customer.created payload: {e}")
        return  # No retry for validation errors

    # Parse to extract needed info
    info = parse_customer_created(data)

    # Execute service
    with get_customer_service() as service:
        service.handle_customer_created(info)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def customer_deleted(self, payload: dict):
    """Handle customer.deleted webhook."""
    # Validate payload structure
    try:
        data = CustomerPayload(**payload)
    except ValidationError as e:
        logger.warning(f"Invalid customer.deleted payload: {e}")
        return  # No retry for validation errors

    # Parse to extract needed info
    info = parse_customer_deleted(data)

    # Execute service
    with get_customer_service() as service:
        service.handle_customer_deleted(info)
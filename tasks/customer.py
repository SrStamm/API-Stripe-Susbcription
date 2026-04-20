from db.session import get_session
from repositories.user_repositories import UserRepository
from services.customer_service import CustomerService
from parsers.customer import (
    CustomerPayload,
    parse_customer_created,
    parse_customer_deleted,
)
from tasks.app import celery_app


def _get_customer_service() -> CustomerService:
    """Create CustomerService instance for Celery tasks."""
    session = next(get_session())
    user_repo = UserRepository(session)
    return CustomerService(user_repo)


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
    data = CustomerPayload(**payload)

    # Parse to extract needed info
    info = parse_customer_created(data)

    # Execute service
    service = _get_customer_service()
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
    data = CustomerPayload(**payload)

    # Parse to extract needed info
    info = parse_customer_deleted(data)

    # Execute service
    service = _get_customer_service()
    service.handle_customer_deleted(info)
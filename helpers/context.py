from contextlib import contextmanager

from db.session import get_session
from repositories.plan_repositories import PlanRepository
from repositories.subscription_repositories import SubscriptionRepository
from repositories.user_repositories import UserRepository
from services.customer_service import CustomerService
from services.subscription_service import SubscriptionService


@contextmanager
def get_subscription_service():
    """Get SubscriptionService with proper session cleanup.

    Usage:
        with get_subscription_service() as service:
            service.handle_invoice_paid(info)
    """
    session = next(get_session())
    try:
        yield SubscriptionService(
            SubscriptionRepository(session),
            UserRepository(session),
            PlanRepository(session),
        )
    finally:
        session.close()


@contextmanager
def get_customer_service():
    """Get CustomerService with proper session cleanup.

    Usage:
        with get_customer_service() as service:
            service.handle_customer_created(info)
    """
    session = next(get_session())
    try:
        yield CustomerService(UserRepository(session))
    finally:
        session.close()
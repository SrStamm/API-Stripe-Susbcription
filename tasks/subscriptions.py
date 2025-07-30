from sqlmodel import true
from db.session import get_session
from repositories.plan_repositories import PlanRepository
from repositories.subscription_repositories import SubscriptionRepository
from core.logger import logger
from datetime import datetime
from repositories.user_repositories import UserRepository
from tasks.app import celery_app
from schemas.exceptions import DatabaseError


@celery_app.task
def customer_sub_basic(payload: dict):
    session = next(get_session())
    sub_repo = SubscriptionRepository(session)
    plan_repo = PlanRepository(session)
    user_repo = UserRepository(session)

    try:
        user = user_repo.get_user_by_customer_id(payload["id"])
        if not user:
            raise

        plan = plan_repo.get_plan_by_plan_id(id=5)
        if not plan:
            raise

        sub_repo.create(
            user_id=user.id,
            plan_id=plan.id,
            subscription_id="sub_free",
            status="free",
            current_period_end=datetime.now(),
        )

        sub_repo.update_for_user(
            sub_id="sub_free",
            customer_id=payload["id"],
            status="active",
            current_period_end=None,
            is_active=True,
        )

        logger.info(f"User {user.id} was suscripted to trial free correctly ")
    except DatabaseError as e:
        raise e


@celery_app.task(
    bind=True,
    autoretry_for=(
        Exception,
        DatabaseError,
    ),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def customer_subscription_created(self, payload: dict):
    session = next(get_session())
    subs_repo = SubscriptionRepository(session)

    try:
        current_period_end = datetime.fromtimestamp(
            payload["items"]["data"][0]["current_period_end"]
        )

        subs_repo.update_for_user(
            sub_id=payload["id"],
            customer_id=payload["customer"],
            status=payload["status"],
            current_period_end=current_period_end,
            is_active=True,
        )
        logger.info(f"Customer subscription {payload['id']} updated correctly")

    except DatabaseError as e:
        logger.error(
            f"Database error in customer_subscription_created for {payload['id']}: {e}"
        )
        raise
    except Exception as e:
        logger.error(f"Error in Customer Subscription Created: {e}")
        raise


@celery_app.task(
    bind=True,
    autoretry_for=(
        Exception,
        DatabaseError,
    ),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def customer_subscription_updated(self, payload: dict):
    session = next(get_session())
    subs_repo = SubscriptionRepository(session)

    try:
        # Obtiene el periodo de finalización de la suscripcion
        current_period_end = datetime.fromtimestamp(
            payload["items"]["data"][0]["current_period_end"]
        )

        subs_repo.update_for_user(
            sub_id=payload["id"],
            customer_id=payload["customer"],
            status=payload["status"],
            current_period_end=current_period_end,
            is_active=True,
        )

        logger.info(f"Customer subscription {payload['id']} updated correctly")

    except DatabaseError as e:
        logger.error(
            f"Database error in customer_subscription_updated for {payload['id']}: {e}"
        )
        raise
    except Exception as e:
        logger.error(f"Error in Customer Subscription Updated: {e}")
        raise


@celery_app.task(
    bind=True,
    autoretry_for=(
        Exception,
        DatabaseError,
    ),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    default_retry_delay=1,
)
def customer_subscription_deleted(self, payload: dict):
    session = next(get_session())
    subs_repo = SubscriptionRepository(session)

    try:
        current_period_end = datetime.fromtimestamp(
            payload["items"]["data"][0]["current_period_end"]
        )

        subs_repo.cancel(
            sub_id=payload["id"],
            customer_id=payload["customer"],
            status=payload["status"],
            current_period_end=current_period_end,
        )
        logger.info(f"Customer subscription {payload['id']} updated correctly")

    except DatabaseError as e:
        logger.error(
            f"Database error in customer_subscription_deleted for {payload['id']}: {e}"
        )
        raise
    except Exception as e:
        logger.error(f"Error in Customer Subscription Deleted: {e}")
        raise

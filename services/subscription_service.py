from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from core.stripe_test import cancelSubscription, createSubscription
from core.logger import logger
from db.session import Session, get_session, SQLAlchemyError, select
from models.user import Users
from models.plan import Plans
from models.subscription import Subscriptions
from repositories.plan_repositories import PlanRepository, get_plan_repo
from repositories.user_repositories import UserRepository, get_user_repository
from repositories.subscription_repositories import (
    SubscriptionRepository,
    get_subs_repo,
)
from schemas.enums import SubscriptionTier, SubscriptionStatus
from schemas.exceptions import (
    PlanNotFound,
    UserNotFoundError,
    DatabaseError,
    UserNotSubscriptedError,
    UserSubscriptedError,
)
from schemas.request import SubID, SubscriptionCreate


# Info classes for task handlers
class InvoicePaidInfo(BaseModel):
    subscription_id: str
    customer_id: str
    current_period_end: datetime
    status: str


class SubscriptionCreatedInfo(BaseModel):
    subscription_id: str
    customer_id: str
    current_period_end: datetime
    status: str


class SubscriptionUpdatedInfo(BaseModel):
    subscription_id: str
    customer_id: str
    current_period_end: datetime
    status: str
    is_active: bool


class SubscriptionDeletedInfo(BaseModel):
    subscription_id: str
    customer_id: str
    current_period_end: datetime
    status: str


class SubscriptionPausedInfo(BaseModel):
    subscription_id: str
    customer_id: str
    status: str


class SubscriptionService:
    def __init__(
        self,
        repo: SubscriptionRepository,
        user_repo: UserRepository,
        plan_repo: PlanRepository,
    ):
        self.repo = repo
        self.user_repo = user_repo
        self.plan_repo = plan_repo

    def get_by_id(self, id: str):
        return self.repo.get_subscription_by_id(id)

    def get_all_subscription(self):
        return self.repo.get_all_subscription()

    def get_all_subscription_by_user(self, id: int):
        return self.repo.get_all_subscription_by_user(id)

    def create(self, data: SubscriptionCreate, user_id: int):
        try:
            # Obtiene el usuario para stripe_customer_id
            user = self.user_repo.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError(user_id)

            # Obtiene el plan y el price_id
            plan = self.plan_repo.get_plan_by_tier(tier=data.tier)
            if not plan:
                raise PlanNotFound("id_not_found")

            # Obtiene todas las suscripciones del usuario
            all_subs = self.repo.get_all_subscription_by_user(user_id)

            # Verifica que el usuario no este subscribed
            for sub in all_subs:
                if sub.tier == data.tier:
                    raise UserSubscriptedError(user_id=user_id, plan_id=plan.id)

            # Crea una nueva suscripción en Stripe
            subs = createSubscription(
                customer_id=user.stripe_customer_id,
                price_id=plan.stripe_price_id,
                user_id=user_id,
                plan_id=plan.id,
            )

            current_period_end = subs["current_period_end"]
            if not current_period_end:
                current_period_end = datetime.now()

            self.repo.create(
                user_id=user_id,
                plan_id=plan.id,
                subscription_id=subs["subscription_id"],
                status=subs["status"],
                tier=data.tier,
                current_period_end=current_period_end,
            )

            return {
                "detail": "Subscription created successfully",
                "subscription_id": subs["subscription_id"],
                "client_secret": subs["clientSecret"],
                "status": "incomplete",
            }
        except DatabaseError as e:
            raise e

    def cancel(self, data: SubID, user_id: int):
        user = self.user_repo.get_user_by_id(user_id)

        sub_found = self.repo.get_subscription_for_user(
            data.id, user.stripe_customer_id
        )

        if not sub_found:
            raise UserNotSubscriptedError(user_id=user_id, sub_id=data.id)

        cancelSubscription(data.id)

        return {
            "detail": f"Subscription {sub_found.id} has been cancelated with success"
        }

    # Celery task handlers
    def _get_existing_subscription(self, sub_id: str, customer_id: str):
        """Get existing subscription or raise exception.

        Helper to avoid code duplication in handlers.
        """
        sub = self.repo.get_subscription_for_user(sub_id=sub_id, customer_id=customer_id)
        if not sub:
            raise Exception(f"Subscription {sub_id} not found")
        return sub

    def handle_customer_sub_basic(self, customer_id: str):
        """Create free trial subscription for user."""
        logger.info(f"Processing customer_sub_basic - customer_id: {customer_id}")

        user = self.user_repo.get_user_by_customer_id(customer_id)
        if not user:
            raise Exception(f"User with stripe_id {customer_id}")

        plan = self.plan_repo.get_plan_by_tier(tier=SubscriptionTier.free)
        if not plan:
            raise Exception('Plan with tier FREE not found')

        self.repo.create(
            user_id=user.id,
            plan_id=plan.id,
            subscription_id="sub_free",
            status=SubscriptionStatus.trialing,
            current_period_end=datetime.now(),
            tier=SubscriptionTier.free,
        )

        self.repo.update_for_user(
            sub_id="sub_free",
            customer_id=customer_id,
            status=SubscriptionStatus.trialing,
            current_period_end=None,
            is_active=True,
        )

        logger.info(f"User {user.id} subscribed to trial free successfully")

    def handle_invoice_paid(self, data: InvoicePaidInfo):
        """Handle invoice.paid webhook - subscription payment succeeded."""
        logger.info(
            f"Processing invoice.paid - sub_id: {data.subscription_id}, customer_id: {data.customer_id}"
        )

        # Uses helper to avoid repetition
        self._get_existing_subscription(data.subscription_id, data.customer_id)

        status = SubscriptionStatus.from_stripe(data.status)

        self.repo.update_for_user(
            sub_id=data.subscription_id,
            customer_id=data.customer_id,
            status=status,
            current_period_end=data.current_period_end,
            is_active=True,
        )

        logger.info(f"Subscription {data.subscription_id} updated successfully")

    def handle_invoice_payment_failed(self, data: InvoicePaidInfo):
        """Handle invoice.payment_failed webhook - subscription payment failed."""
        logger.info(
            f"Processing invoice.payment_failed - sub_id: {data.subscription_id}, customer_id: {data.customer_id}"
        )

        # Uses helper to avoid repetition
        self._get_existing_subscription(data.subscription_id, data.customer_id)

        self.repo.update_for_user(
            sub_id=data.subscription_id,
            customer_id=data.customer_id,
            status=SubscriptionStatus.past_due,
            current_period_end=data.current_period_end,
            is_active=False,
        )

        logger.info(f"Subscription {data.subscription_id} marked as past_due")

    def handle_customer_subscription_created(self, data: SubscriptionCreatedInfo):
        """Handle customer.subscription.created webhook."""
        logger.info(
            f"Processing customer.subscription.created - sub_id: {data.subscription_id}"
        )

        status = SubscriptionStatus.from_stripe(data.status)

        self.repo.update_for_user(
            sub_id=data.subscription_id,
            customer_id=data.customer_id,
            status=status,
            current_period_end=data.current_period_end,
            is_active=True,
        )

        logger.info(f"Subscription {data.subscription_id} created successfully")

    def handle_customer_subscription_updated(self, data: SubscriptionUpdatedInfo):
        """Handle customer.subscription.updated webhook."""
        logger.info(
            f"Processing customer.subscription.updated - sub_id: {data.subscription_id}"
        )

        status = SubscriptionStatus.from_stripe(data.status)

        self.repo.update_for_user(
            sub_id=data.subscription_id,
            customer_id=data.customer_id,
            status=status,
            current_period_end=data.current_period_end,
            is_active=data.is_active,
        )

        logger.info(f"Subscription {data.subscription_id} updated successfully")

    def handle_customer_subscription_deleted(self, data: SubscriptionDeletedInfo):
        """Handle customer.subscription.deleted webhook."""
        logger.info(
            f"Processing customer.subscription.deleted - sub_id: {data.subscription_id}"
        )

        status = SubscriptionStatus.from_stripe(data.status)

        self.repo.cancel(
            sub_id=data.subscription_id,
            customer_id=data.customer_id,
            status=status,
            current_period_end=data.current_period_end,
        )

        logger.info(f"Subscription {data.subscription_id} cancelled successfully")

    def handle_customer_subscription_paused(self, data: SubscriptionPausedInfo):
        """Handle customer.subscription.paused webhook."""
        logger.info(
            f"Processing customer.subscription.paused - sub_id: {data.subscription_id}"
        )

        status = SubscriptionStatus.from_stripe(data.status)

        self.repo.update_for_user(
            sub_id=data.subscription_id,
            customer_id=data.customer_id,
            status=status,
            current_period_end=None,
            is_active=False,
        )

        logger.info(f"Subscription {data.subscription_id} paused successfully")


def get_subs_service(
    repo: SubscriptionRepository = Depends(get_subs_repo),
    user_repo: UserRepository = Depends(get_user_repository),
    plan_repo: PlanRepository = Depends(get_plan_repo),
) -> SubscriptionService:
    return SubscriptionService(repo, user_repo, plan_repo)
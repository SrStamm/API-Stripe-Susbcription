from fastapi import Depends, HTTPException
from repositories.plan_repositories import PlanRepository, get_plan_repo
from repositories.user_repositories import UserRepository, get_user_repository
from repositories.subscription_repositories import SubscriptionRepository, get_subs_repo
from schemas.request import SubID, SubscriptionCreate
from schemas.exceptions import (
    PlanNotFound,
    UserNotFoundError,
    DatabaseError,
    UserNotSubscriptedError,
    UserSubscriptedError,
)
from core.stripe_test import cancelSubscription, createSubscription
from datetime import datetime


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

            # Verifica que el usuario no este suscrito
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


def get_subs_service(
    repo: SubscriptionRepository = Depends(get_subs_repo),
    user_repo: UserRepository = Depends(get_user_repository),
    plan_repo: PlanRepository = Depends(get_plan_repo),
) -> SubscriptionService:
    return SubscriptionService(repo, user_repo, plan_repo)

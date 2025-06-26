from datetime import datetime
from fastapi import Depends, HTTPException
from core.stripe_test import createSubscription, get_price
from repositories.plan_repositories import PlanRepository, get_plan_repo
from repositories.subscription_repositories import SubscriptionRepository, get_subs_repo
from repositories.user_repositories import UserRepository, get_user_repository
from schemas.request import SubscriptionCreate
from schemas.exceptions import UserNotFoundError


class SubscriptionService:
    def __init__(
        self,
        repo: SubscriptionRepository,
        user_repo: UserRepository,
        plan_repo: PlanRepository,
    ) -> None:
        self.repo = repo
        self.user_repo = user_repo
        self.plan_repo = plan_repo

    def get_by_id(self, id: str):
        return self.repo.get_subscription_by_id(id)

    def get_all_subscription(self):
        return self.repo.get_all_subscription()

    def create(self, data: SubscriptionCreate, user_id: int):
        # Obtiene el usuario para stripe_customer_id
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Obtiene el plan y el price_id
        plan = self.plan_repo.get_plan_by_plan_id(data.plan_id)
        if not plan:
            raise HTTPException(404, detail="Plan not found")

        # Crea una nueva suscripción en Stripe
        subs = createSubscription(
            customer_id=user.stripe_customer_id, price_id=plan.stripe_price_id
        )

        current_period_end = subs["current_period_end"]
        if not current_period_end:
            current_period_end = datetime.now()

        self.repo.create(
            user_id=user_id,
            plan_id=data.plan_id,
            subscription_id=subs["subscription_id"],
            status=subs["status"],
            current_period_end=current_period_end,
        )

        return {
            "detail": "User suscripted with success",
            "client_secret": subs["clientSecret"],
        }


def get_subs_service(
    repo: SubscriptionRepository = Depends(get_subs_repo),
    user_repo: UserRepository = Depends(get_user_repository),
    plan_repo: PlanRepository = Depends(get_plan_repo),
) -> SubscriptionService:
    return SubscriptionService(repo, user_repo, plan_repo)

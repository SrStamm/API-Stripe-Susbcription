from schemas.enums import SubscriptionTier
from fastapi import Depends
from models.user import ReadUser
from dependencies.auth import get_current_user
from schemas.exceptions import InsufficientSubscriptionError
from services.subscription_service import SubscriptionService, get_subs_service


def require_subscription_tier(min_tier: SubscriptionTier):
    def dependency(
        user: ReadUser = Depends(get_current_user),
        sub_serv: SubscriptionService = Depends(get_subs_service),
    ):
        user_subs = sub_serv.get_all_subscription_by_user(id=user.id)

        user_tier = SubscriptionTier(value=user_subs[0].tier)

        if not user_tier.has_access_to(min_tier):
            raise InsufficientSubscriptionError(
                user_tier=user_tier, expected_tier=min_tier
            )
        return user

    return dependency

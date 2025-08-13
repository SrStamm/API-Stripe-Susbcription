from fastapi import APIRouter, Depends
from core.sub_verifier import require_subscription_tier
from models.user import ReadUser
from schemas.enums import SubscriptionTier

router = APIRouter(prefix="/products")


@router.get("/free")
def free_tier(
    user: ReadUser = Depends(require_subscription_tier(min_tier=SubscriptionTier.free)),
):
    return {"detail": f"User {user.id} tier is Free, you have access to this level."}


@router.get("/pro")
def pro_tier(
    user: ReadUser = Depends(require_subscription_tier(min_tier=SubscriptionTier.pro)),
):
    return {"detail": f"User {user.id} tier is Pro, you have access to this level."}


@router.get("/enterprise")
def enterprise_tier(
    user: ReadUser = Depends(
        require_subscription_tier(min_tier=SubscriptionTier.enterprise)
    ),
):
    return {
        "detail": f"User {user.id} tier is Enterprise, you have access to this level."
    }

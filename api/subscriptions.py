from fastapi import APIRouter, Depends
from schemas.request import SubID, SubscriptionCreate
from services.subscription_service import SubscriptionService, get_subs_service
from models.user import ReadUser
from dependencies.auth import get_current_user

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/all")
def get_all(serv: SubscriptionService = Depends(get_subs_service)):
    return serv.get_all_subscription()


@router.get("/me")
def get_all_by_user(
    user: ReadUser = Depends(get_current_user),
    serv: SubscriptionService = Depends(get_subs_service),
):
    return serv.get_all_subscription_by_user(user.id)


@router.get("/{id}")
def get_by_id(id: str, serv: SubscriptionService = Depends(get_subs_service)):
    return serv.get_by_id(id)


@router.post("/")
def create(
    new_data: SubscriptionCreate,
    user: ReadUser = Depends(get_current_user),
    serv: SubscriptionService = Depends(get_subs_service),
):
    return serv.create(data=new_data, user_id=user.id)


@router.delete("/")
def cancel(
    id: SubID,
    user: ReadUser = Depends(get_current_user),
    serv: SubscriptionService = Depends(get_subs_service),
):
    return serv.cancel(id, user.id)

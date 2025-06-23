from fastapi import APIRouter, Depends
from services.subscription_service import SubscriptionService, get_subs_service

router = APIRouter()


@router.get("/subscriptions/")
def get_by_id(id: str, serv: SubscriptionService = Depends(get_subs_service)):
    return serv.get_by_id(id)


@router.get("/subscriptions/all")
def get_all(serv: SubscriptionService = Depends(get_subs_service)):
    return serv.get_all_subscription()

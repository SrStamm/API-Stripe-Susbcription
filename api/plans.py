from fastapi import APIRouter, Depends
from services.plan_service import PlanService, get_plan_serv
from schemas.request import PlanCreate, PlanUpdate

router = APIRouter(prefix="/plans")


@router.get("/")
def get_plans(serv: PlanService = Depends(get_plan_serv)):
    return serv.get_all_plans()


@router.post("/")
def create_plan(
    data: PlanCreate,
    serv: PlanService = Depends(get_plan_serv),
):
    return serv.create(
        name=data.name,
        description=data.description,
        amount=data.amount,
        money=data.money,
    )


@router.patch("/")
def update_price_for_plan(
    data: PlanUpdate,
    serv: PlanService = Depends(get_plan_serv),
):
    return serv.update_only_price(
        id=data.id,
        amount=data.amount,
        money=data.money,
    )

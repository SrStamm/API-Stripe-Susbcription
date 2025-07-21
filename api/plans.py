from fastapi import APIRouter, Depends
from services.plan_service import PlanService, get_plan_serv
from schemas.request import PlanCreate, PlanUpdate, PlanID

router = APIRouter(prefix="/plans", tags=["plans"])


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
    return serv.update(
        id=data.id,
        amount=data.amount,
        money=data.money,
        name=data.name,
        description=data.description,
    )


@router.delete("/")
def deactivate_plan(data: PlanID, serv: PlanService = Depends(get_plan_serv)):
    return serv.deactivate_plan(data.id)

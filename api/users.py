from fastapi import APIRouter, Depends
from dependencies.auth import get_current_user
from schemas.exceptions import CustomerIdError
from services.user_service import get_user_service, UserService
from models.user import CreateUser, ReadUser

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
def get_users(serv: UserService = Depends(get_user_service)):
    return serv.get_users()


@router.get("/me")
def get_user_me(
    user: ReadUser = Depends(get_current_user),
    serv: UserService = Depends(get_user_service),
):
    return serv.get_user_me(user.id)


@router.post("/")
def create_user(email: CreateUser, serv: UserService = Depends(get_user_service)):
    print(f"Received email: {email}")
    return serv.create(email)


@router.delete("/")
def delete_user(
    user: ReadUser = Depends(get_current_user),
    serv: UserService = Depends(get_user_service),
):
    if not user.stripe_customer_id:
        raise CustomerIdError(user_id=user.id)

    return serv.delete(user.stripe_customer_id)

from fastapi import APIRouter, Depends
from dependencies.auth import get_current_user
from services.user_service import get_user_service, UserService
from models.user import CreateUser, ReadUser

router = APIRouter()


@router.get("/users/")
def get_users(serv: UserService = Depends(get_user_service)):
    return serv.get_users()


@router.get("/users/me")
def get_user_me(
    user: ReadUser = Depends(get_current_user),
    serv: UserService = Depends(get_user_service),
):
    return serv.get_user_me(user.id)


@router.post("/users/")
def create_user(email: CreateUser, serv: UserService = Depends(get_user_service)):
    print(f"Received email: {email}")
    return serv.create(email)

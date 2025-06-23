from fastapi import APIRouter, Depends
from services.user_service import get_user_service, UserService
from models.user import CreateUser

router = APIRouter()


@router.get("/users/")
def get_users(serv: UserService = Depends(get_user_service)):
    return serv.get_users()


@router.post("/users/")
def create_user(email: CreateUser, serv: UserService = Depends(get_user_service)):
    print(f"Received email: {email}")
    return serv.create(email)

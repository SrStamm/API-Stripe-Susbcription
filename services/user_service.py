from fastapi import Depends
from pydantic import EmailStr
from models.user import CreateUser
from repositories.user_repositories import UserRepository, get_user_repository
from core.stripe_test import createCustomer


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get_user_me(self, id: int):
        return self.repo.get_user_by_id(id)

    def get_users(self):
        results = self.repo.get_users()
        return results

    def create(self, data: CreateUser):
        email: EmailStr = data.email
        user = self.repo.get_user_by_email(email)

        if not user:
            customer = self.repo.create(email)

            stripe_customer = createCustomer(email, customer.id)

            self.repo.update(id=customer.id, stripe_id=stripe_customer["id"])

            return {"detail": "User created"}
        else:
            return {"detail": "User with these email exist"}


def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repo)

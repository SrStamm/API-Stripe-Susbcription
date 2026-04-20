from pydantic import BaseModel
from fastapi import Depends

from core.logger import logger
from db.session import Session, get_session, SQLAlchemyError
from models.user import Users
from repositories.user_repositories import UserRepository, get_user_repository
from schemas.exceptions import DatabaseError


# Info classes for task handlers
class CustomerCreatedInfo(BaseModel):
    stripe_id: str
    email: str


class CustomerDeletedInfo(BaseModel):
    stripe_id: str


class CustomerService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def handle_customer_created(self, data: CustomerCreatedInfo):
        """Handle customer.created webhook - creates or updates user."""
        logger.info(f"Processing customer.created - stripe_id: {data.stripe_id}")

        user = self.user_repo.get_user_by_customer_id(data.stripe_id)

        if not user:
            user = self.user_repo.create(email=data.email)
            self.user_repo.update(id=user.id, stripe_id=data.stripe_id)
            logger.info(f"Created new user {user.id} for customer {data.stripe_id}")
        else:
            logger.info(f"User {user.id} already exists for customer {data.stripe_id}")

    def handle_customer_deleted(self, data: CustomerDeletedInfo):
        """Handle customer.deleted webhook - deletes user."""
        logger.info(f"Processing customer.deleted - stripe_id: {data.stripe_id}")

        self.user_repo.delete(data.stripe_id)
        logger.info(f"Deleted user for customer {data.stripe_id}")


def get_customer_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> CustomerService:
    return CustomerService(user_repo)
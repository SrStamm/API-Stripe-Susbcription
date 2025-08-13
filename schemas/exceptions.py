from fastapi import HTTPException, status
from sqlalchemy.sql.coercions import expect_col_expression_collection

from models import user
from schemas.enums import SubscriptionTier


class NotAuthorized(HTTPException):
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User with user_id {user_id} is Not Authorized",
        )


class InvalidToken(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Not Authorized"
        )


class UserNotFoundInLogin(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


class LoginError(HTTPException):
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password incorrect"
        )


class UserWithEmailExist(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Ya existe un usuario con este Email",
        )


class UserNotFoundError(HTTPException):
    def __init__(self, id):
        self.id = id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found"
        )


class DatabaseError(HTTPException):
    def __init__(self, error, func: str):
        self.error = error
        self.func = func
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"database error en {func}: {str(error)}",
        )


class SessionNotFound(HTTPException):
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found for user"
        )


class SubscriptionNotFound(HTTPException):
    def __init__(self, sub_id: str):
        self.sub_id = sub_id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription {sub_id} not found",
        )


class PlanNotFound(HTTPException):
    def __init__(self, id: str):
        self.id = id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {id} not found",
        )


class ProductNotFound(HTTPException):
    def __init__(self, id: str):
        self.id = id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {id} not found",
        )


class PriceNotFound(HTTPException):
    def __init__(self, id: str):
        self.id = id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Price to product {id} not found",
        )


class CustomerIdError(HTTPException):
    def __init__(self, user_id: int):
        self.user_id = user_id

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_id} not have CustomerId to Stripe",
        )


class UserSubscriptedError(HTTPException):
    def __init__(self, user_id: int, plan_id: int):
        self.user_id = user_id
        self.plan_id = plan_id
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_id} us subscripted to plan {plan_id}",
        )


class UserNotSubscriptedError(HTTPException):
    def __init__(self, user_id: int, sub_id: str):
        self.user_id = user_id
        self.sub_id = sub_id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} is not subscripted to plan {sub_id}",
        )


class InsufficientSubscriptionError(HTTPException):
    def __init__(self, user_tier: SubscriptionTier, expected_tier: SubscriptionTier):
        self.user_tier = user_tier
        self.expected_tier = expected_tier
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User with tier {user_tier.value} is not sufficient. Need for minimun {expected_tier.value} to access",
        )

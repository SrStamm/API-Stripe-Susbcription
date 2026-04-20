from typing import Optional

from pydantic import BaseModel


# Validation schema - validates payload structure
# Make fields optional - validation logic is in the parser
class CustomerPayload(BaseModel):
    id: str
    email: Optional[str] = None


# Parsed info returned to service
class CustomerCreatedInfo(BaseModel):
    stripe_id: str
    email: str


class CustomerDeletedInfo(BaseModel):
    stripe_id: str


def parse_customer_created(payload: CustomerPayload) -> CustomerCreatedInfo:
    """Parse customer.created webhook payload."""
    return CustomerCreatedInfo(
        stripe_id=payload.id,
        email=payload.email,
    )


def parse_customer_deleted(payload: CustomerPayload) -> CustomerDeletedInfo:
    """Parse customer.deleted webhook payload."""
    return CustomerDeletedInfo(
        stripe_id=payload.id,
    )
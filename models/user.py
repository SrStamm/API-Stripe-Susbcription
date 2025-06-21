from typing import List, Optional, TYPE_CHECKING
from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .subscription import Subscriptions


class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr
    stripe_customer_id: Optional[str]

    subscriptions: List["Subscriptions"] = Relationship(back_populates="user")

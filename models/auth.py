from sqlmodel import SQLModel, Field
from datetime import datetime as dt, timezone


class Sessions(SQLModel, table=True):
    jti: str = Field(primary_key=True, max_length=36)
    sub: str = Field(index=True)

    is_active: bool = Field(default=True)
    use_count: int = Field(default=0, ge=0)

    created_at: dt = Field(default_factory=lambda: dt.now(timezone.utc))
    expires_at: dt

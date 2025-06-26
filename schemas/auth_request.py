from pydantic import BaseModel, EmailStr, Field


class FormEmail(BaseModel):
    email: EmailStr


class Token(BaseModel):
    access_token: str = Field(examples=[])
    token_type: str = Field(examples=["bearer"])
    refresh_token: str


class Access_Token(BaseModel):
    access_token: str = Field(examples=[])
    token_type: str = Field(examples=["bearer"])


class RefreshTokenRequest(BaseModel):
    refresh: str

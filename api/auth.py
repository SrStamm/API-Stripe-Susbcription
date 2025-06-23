from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
from dependencies.auth import get_auth_serv, AuthService, get_current_user
from models.user import Users
import os
from core.logger import logger
from schemas.exceptions import DatabaseError, InvalidToken
from schemas.auth_request import Token, RefreshTokenRequest
from schemas.responses import NotFound, DatabaseErrorResponse

router = APIRouter(tags=["Login"])

# Duracion de los tokens
ACCESS_TOKEN_DURATION = int(os.environ.get("ACCESS_TOKEN_DURATION", "15"))
REFRESH_TOKEN_DURATION = int(os.environ.get("REFRESH_TOKEN_DURATION", "7"))

ALGORITHM = os.environ.get("ALGORITHM")

SECRET = os.environ.get("SECRET_KEY")

crypt = CryptContext(schemes=["bcrypt"])

oauth2 = OAuth2PasswordBearer(tokenUrl="token", scheme_name="Bearer")


@router.post(
    "/login",
    description="Login path. You need a username and password. First need to create a user",
)
# @limiter.limit("10/minute")
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    auth_serv: AuthService = Depends(get_auth_serv),
):
    try:
        return await auth_serv.login(form)
    except DatabaseError:
        logger.error("[login] Database Error")
        raise


@router.post(
    "/refresh",
    description="Refresh path for obtain a new token. You need a refresh token.",
)
# @limiter.limit("10/minute")
async def refresh(
    refresh: RefreshTokenRequest,
    request: Request,
    auth_serv: AuthService = Depends(get_auth_serv),
) -> Token:
    try:
        return auth_serv.refresh(refresh)
    except JWTError as e:
        logger.error(f"[refresh] Invalid Token during refresh | Error :{str(e)}")
        if hasattr(e, "claims"):
            logger.error(f"Problematic claims: {e.claims}")
        raise InvalidToken

    except DatabaseError:
        logger.error("[refresh] Database Error")
        raise


@router.post(
    "/logout",
    description="Logout path to close session. Close all user sessions ",
)
# @limiter.limit("10/minute")
async def logout(
    request: Request,
    user: Users = Depends(get_current_user),
    auth_serv: AuthService = Depends(get_auth_serv),
):
    try:
        return auth_serv.logout(user.id)
    except DatabaseError:
        logger.error("[logout] Database Error")
        raise


@router.get("/expired")
def get_expired_sessions(auth_serv: AuthService = Depends(get_auth_serv)):
    try:
        return auth_serv.get_expired_sessions()
    except SQLAlchemyError as e:
        logger.error(f"[get_expired_sessions] Database Error | Error: {str(e)}")
        raise DatabaseError(e, func="get_expired_sessions")

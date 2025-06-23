from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_services import AuthService, get_auth_serv
from schemas.exceptions import UserNotFoundError, InvalidToken

security = HTTPBearer()


def get_current_user(
    auth_serv: AuthService = Depends(get_auth_serv),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        return auth_serv.auth_user(credentials.credentials)
    except UserNotFoundError:
        raise
    except InvalidToken:
        raise

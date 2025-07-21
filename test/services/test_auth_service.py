from jose import JWTError
import pytest
from models.auth import Sessions
from models.user import Users
from schemas.auth_request import RefreshTokenRequest, Token
from schemas.exceptions import (
    DatabaseError,
    InvalidToken,
    SessionNotFound,
    UserNotFoundError,
    UserNotFoundInLogin,
)
from services.auth_services import AuthService
from datetime import datetime as dt, timedelta, timezone
from sqlalchemy.exc import SQLAlchemyError


def test_get_expired_sessions_found(mocker):
    mock_auth_repo = mocker.Mock()

    # Mockea las respuestas
    mock_expires_at = dt(2024, 10, 10, 0, 0)
    mock_expired_session = Sessions(
        jti="jti_mock",
        sub="sub_mock",
        is_active=False,
        use_count=0,
        expires_at=mock_expires_at,
    )

    mock_auth_repo.get_expired_sessions.return_value = [mock_expired_session]

    serv = AuthService(mock_auth_repo)

    serv.get_expired_sessions()

    mock_auth_repo.get_expired_sessions.assert_called_once_with()


def test_get_expired_sessions_not_found(mocker):
    mock_auth_repo = mocker.Mock()

    mock_auth_repo.get_expired_sessions.return_value = None

    serv = AuthService(mock_auth_repo)

    response = serv.get_expired_sessions()

    assert response == {"detail": "No expired sessions"}

    mock_auth_repo.get_expired_sessions.assert_called_once_with()


def test_get_expired_sessions_exception(mocker):
    mock_auth_repo = mocker.Mock()

    mock_auth_repo.get_expired_sessions.side_effect = Exception(
        "Simuled Exception Error"
    )

    serv = AuthService(mock_auth_repo)

    with pytest.raises(Exception):
        serv.get_expired_sessions()

    mock_auth_repo.get_expired_sessions.assert_called_once_with()


def test_auth_user_error(mocker):
    mock_repo = mocker.Mock()
    mock_token = mocker.Mock()

    serv = AuthService(mock_repo)

    mocker.patch("services.auth_services.jwt.decode", side_effect=InvalidToken)

    with pytest.raises(InvalidToken):
        serv.auth_user(mock_token)


def test_auth_user_JWTError(mocker):
    mock_repo = mocker.Mock()
    mock_token = mocker.Mock()

    serv = AuthService(mock_repo)

    mocker.patch("services.auth_services.jwt.decode", side_effect=JWTError)

    with pytest.raises(InvalidToken):
        serv.auth_user(mock_token)


def test_auth_user_scope_error(mocker):
    mock_repo = mocker.Mock()
    mock_token = mocker.Mock()

    serv = AuthService(mock_repo)

    mock_payload = {}

    mocker.patch("services.auth_services.jwt.decode", return_value=mock_payload)

    with pytest.raises(InvalidToken):
        serv.auth_user(mock_token)


def test_auth_user_sub_error(mocker):
    mock_repo = mocker.Mock()
    mock_token = mocker.Mock()

    serv = AuthService(mock_repo)

    expiration_time = dt.now(timezone.utc) + timedelta(hours=1)
    mock_payload = {"exp": expiration_time.timestamp(), "scope": "api_access"}

    mocker.patch("services.auth_services.jwt.decode", return_value=mock_payload)

    with pytest.raises(InvalidToken):
        serv.auth_user(mock_token)


def test_auth_user_not_found_error(mocker):
    mock_repo = mocker.Mock()
    mock_token = mocker.Mock()

    mock_payload = {"sub": "test@gmail.com", "scope": "api_access"}

    mocker.patch("services.auth_services.jwt.decode", return_value=mock_payload)

    mock_repo.get_user_whit_email.return_value = None

    serv = AuthService(mock_repo)

    with pytest.raises(UserNotFoundError):
        serv.auth_user(mock_token)


def test_auth_user_exp_error(mocker):
    mock_repo = mocker.Mock()
    mock_token = mocker.Mock()

    serv = AuthService(mock_repo)

    mock_payload = {"sub": "1", "scope": "api_access"}

    mocker.patch("services.auth_services.jwt.decode", return_value=mock_payload)

    mock_repo.get_user_by_id.return_value = None
    with pytest.raises(InvalidToken):
        serv.auth_user(mock_token)


def test_auth_user_token_expired_error(mocker):
    mock_repo = mocker.Mock()
    mock_token = mocker.Mock()

    expiration_time = dt.now(timezone.utc) - timedelta(hours=1)
    mock_payload = {
        "sub": "1",
        "scope": "api_access",
        "exp": expiration_time.timestamp(),
    }

    mocker.patch("services.auth_services.jwt.decode", return_value=mock_payload)

    mock_repo.get_user_by_id.return_value = None

    serv = AuthService(mock_repo)

    with pytest.raises(InvalidToken):
        serv.auth_user(mock_token)


def test_auth_user_jwt_error(mocker):
    mock_repo = mocker.Mock()
    mock_token = mocker.Mock()

    mocker.patch("services.auth_services.jwt.decode", side_effect=InvalidToken())

    mock_repo.get_user_by_id.return_value = None

    serv = AuthService(mock_repo)

    with pytest.raises(InvalidToken):
        serv.auth_user(mock_token)


async def test_login_user_not_found(mocker):
    mocker_repo = mocker.Mock()

    mocker_repo.get_user_whit_email.return_value = None

    serv = AuthService(mocker_repo)

    with pytest.raises(UserNotFoundInLogin):
        await serv.login("test@gmail.com")


async def test_login_db_error(mocker):
    mocker_repo = mocker.Mock()

    expiration_time = dt.now(timezone.utc) - timedelta(hours=1)
    mock_user = Users(id=1, email="test@gmail.com", stripe_customer_id="cus_mock_id")

    mocker_repo.get_user_whit_email.return_value = mock_user

    mock_payload = {
        "sub": "1",
        "scope": "api_access",
        "exp": expiration_time.timestamp(),
    }

    mocker.patch("services.auth_services.jwt.decode", return_value=mock_payload)

    mocker_repo.new_session.side_effect = DatabaseError(
        error=Exception("Simuled DB error"), func="AuthRepository.new_session"
    )

    serv = AuthService(mocker_repo)

    with pytest.raises(DatabaseError):
        await serv.login("test@gmail.com")


def test_logout_sessions_not_found(mocker):
    mock_repo = mocker.Mock()

    serv = AuthService(mock_repo)

    mock_repo.get_active_sessions.return_value = None

    with pytest.raises(SessionNotFound):
        serv.logout("sub_mock")

    mock_repo.get_active_sessions.side_effect = DatabaseError(
        SQLAlchemyError("db error"), "logout"
    )

    with pytest.raises(DatabaseError):
        serv.logout("sub_mock")


def test_logout_sessions_success(mocker):
    mock_repo = mocker.Mock()

    mock_expires_at = dt(2024, 10, 10, 0, 0)

    mock_session = Sessions(
        jti="jti_mock",
        sub="sub_mock",
        is_active=False,
        use_count=0,
        expires_at=mock_expires_at,
    )

    mock_repo.get_active_sessions.return_value = [mock_session]

    mock_repo.delete_session.return_value = None

    serv = AuthService(mock_repo)

    response = serv.logout("sub_mock")

    assert response == {"detail": "Closed all sessions"}

    mock_repo.delete_session.assert_called_once_with(mock_session)


def test_refresh_not_session(mocker):
    mock_repo = mocker.Mock()
    mock_token = mocker.Mock()

    # Mockea jtw.get_unverified_claims
    mocker.patch(
        "services.auth_services.jwt.get_unverified_claims",
        return_value={"jti": "jti_mocked"},
    )

    mock_repo.get_session_with_jti.return_value = None

    serv = AuthService(mock_repo)

    with pytest.raises(InvalidToken):
        serv.refresh(mock_token)

    mock_repo.get_session_with_jti.assert_called_once_with("jti_mocked")


def test_refresh_not_scope(mocker):
    mock_repo = mocker.Mock()
    mock_token = mocker.Mock()

    mock_payload = {"jti": "jti_mocked"}

    mocker.patch(
        "services.auth_services.jwt.get_unverified_claims",
        return_value=mock_payload,
    )

    # Mockea jwt.decode
    mocker.patch(
        "services.auth_services.jwt.decode",
        return_value=mock_payload,
    )

    mock_repo.get_session_with_jti.return_value = mock_payload

    serv = AuthService(mock_repo)

    with pytest.raises(InvalidToken):
        serv.refresh(mock_token)

    mock_repo.get_session_with_jti.assert_called_once_with("jti_mocked")


def test_refresh_scope_error(mocker):
    mock_repo = mocker.Mock()
    mock_token = mocker.Mock()

    mock_payload = {"jti": "jti_mocked", "scope": "api_token"}

    mocker.patch(
        "services.auth_services.jwt.get_unverified_claims",
        return_value=mock_payload,
    )

    # Mockea jwt.decode
    mocker.patch(
        "services.auth_services.jwt.decode",
        return_value=mock_payload,
    )

    mock_repo.get_session_with_jti.return_value = mock_payload

    serv = AuthService(mock_repo)

    with pytest.raises(InvalidToken):
        serv.refresh(mock_token)

    mock_repo.get_session_with_jti.assert_called_once_with("jti_mocked")


def test_refresh_not_sub(mocker):
    mock_repo = mocker.Mock()
    mock_token = mocker.Mock()

    mock_payload = {"jti": "jti_mocked", "scope": "token_refresh"}

    mocker.patch(
        "services.auth_services.jwt.get_unverified_claims",
        return_value=mock_payload,
    )

    # Mockea jwt.decode
    mocker.patch(
        "services.auth_services.jwt.decode",
        return_value=mock_payload,
    )

    mock_repo.get_session_with_jti.return_value = mock_payload

    serv = AuthService(mock_repo)

    with pytest.raises(InvalidToken):
        serv.refresh(mock_token)

    mock_repo.get_session_with_jti.assert_called_once_with("jti_mocked")


def test_refresh_user_not_found(mocker):
    mock_repo = mocker.Mock()
    mock_token = mocker.Mock()

    mock_payload = {
        "jti": "jti_mocked",
        "scope": "token_refresh",
        "sub": "test@gmail.com",
    }

    mocker.patch(
        "services.auth_services.jwt.get_unverified_claims",
        return_value=mock_payload,
    )

    # Mockea jwt.decode
    mocker.patch(
        "services.auth_services.jwt.decode",
        return_value=mock_payload,
    )

    mock_repo.get_session_with_jti.return_value = mock_payload

    mock_repo.get_user_whit_email.return_value = None

    serv = AuthService(mock_repo)

    with pytest.raises(UserNotFoundError):
        serv.refresh(mock_token)

    mock_repo.get_session_with_jti.assert_called_once_with("jti_mocked")
    mock_repo.get_user_whit_email.assert_called_once_with("test@gmail.com")


def test_refresh_not_exp(mocker):
    mock_repo = mocker.Mock()
    mock_token = mocker.Mock()
    mock_user = mocker.Mock()

    mock_payload = {
        "jti": "jti_mocked",
        "scope": "token_refresh",
        "sub": "test@gmail.com",
    }

    mocker.patch(
        "services.auth_services.jwt.get_unverified_claims",
        return_value=mock_payload,
    )

    # Mockea jwt.decode
    mocker.patch(
        "services.auth_services.jwt.decode",
        return_value=mock_payload,
    )

    mock_repo.get_session_with_jti.return_value = mock_payload

    mock_repo.get_user_whit_email.return_value = mock_user

    serv = AuthService(mock_repo)

    with pytest.raises(InvalidToken):
        serv.refresh(mock_token)

    mock_repo.get_session_with_jti.assert_called_once_with("jti_mocked")
    mock_repo.get_user_whit_email.assert_called_once_with("test@gmail.com")


def test_refresh_token_expired(mocker):
    mock_repo = mocker.Mock()
    mock_token = mocker.Mock()
    mock_user = mocker.Mock()

    mock_expires_at = dt.now()

    mock_payload = {
        "jti": "jti_mocked",
        "scope": "token_refresh",
        "sub": "test@gmail.com",
        "exp": int(mock_expires_at.timestamp()),
    }

    mocker.patch(
        "services.auth_services.jwt.get_unverified_claims",
        return_value=mock_payload,
    )

    # Mockea jwt.decode
    mocker.patch(
        "services.auth_services.jwt.decode",
        return_value=mock_payload,
    )

    mock_repo.get_session_with_jti.return_value = mock_payload

    mock_repo.get_user_whit_email.return_value = mock_user

    serv = AuthService(mock_repo)

    with pytest.raises(InvalidToken):
        serv.refresh(mock_token)

    mock_repo.get_session_with_jti.assert_called_once_with("jti_mocked")
    mock_repo.get_user_whit_email.assert_called_once_with("test@gmail.com")


def test_refresh_db_error(mocker):
    mock_repo = mocker.Mock()
    mock_token = "mock_jwt_token"

    mock_user = Users(id=1, email="test@gmail.com", stripe_customer_id="cus_mock_id")

    mock_expires_at = dt.now() + timedelta(hours=1)

    mock_payload = {
        "jti": "jti_mocked",
        "scope": "token_refresh",
        "sub": "test@gmail.com",
        "exp": int(mock_expires_at.timestamp()),
    }

    mocker.patch(
        "services.auth_services.jwt.get_unverified_claims",
        return_value=mock_payload,
    )

    mocker.patch(
        "services.auth_services.jwt.decode",
        return_value=mock_payload,
    )

    mock_repo.get_session_with_jti.return_value = mock_payload

    mock_repo.get_user_whit_email.return_value = mock_user

    mock_repo.delete_session.side_effect = DatabaseError(
        error=Exception("Simuled db error"), func="AuthRepository.delete_session"
    )

    serv = AuthService(mock_repo)

    with pytest.raises(DatabaseError):
        serv.refresh(refresh=RefreshTokenRequest(refresh=mock_token))

    mock_repo.get_session_with_jti.assert_called_once_with("jti_mocked")
    mock_repo.get_user_whit_email.assert_called_once_with("test@gmail.com")
    mock_repo.delete_session.assert_called_once_with(mock_payload)


def test_refresh_jwt_error(mocker):
    mock_repo = mocker.Mock()
    mock_token = "mock_jwt_token"

    mock_payload = {"jti": "jti_mocked", "sub": "test@gmail.com"}

    mocker.patch(
        "services.auth_services.jwt.get_unverified_claims",
        return_value=mock_payload,
    )

    mocker.patch("services.auth_services.jwt.decode", side_effect=JWTError())

    mock_repo.get_session_with_jti.return_value = mock_payload

    serv = AuthService(mock_repo)

    with pytest.raises(InvalidToken):
        serv.refresh(refresh=RefreshTokenRequest(refresh=mock_token))

    mock_repo.get_session_with_jti.assert_called_once_with("jti_mocked")


def test_refresh_success(mocker):
    # Configurar mocks y datos de prueba
    mock_repo = mocker.Mock()
    mock_refresh_token = "mock_jwt_token"
    mock_email = "test@gmail.com"
    mock_jti = "mock_jti"
    mock_access_token = "mock_access_token"
    mock_new_refresh_token = "mock_new_refresh_token"

    # Configurar payloads
    mock_unverified_payload = {
        "jti": mock_jti,
        "scope": "token_refresh",
        "sub": mock_email,
        "exp": (dt.now(timezone.utc) + timedelta(hours=1)).timestamp(),
    }

    mock_decoded_payload = mock_unverified_payload.copy()

    # COnfigurar usuario simulado
    mock_user = Users(id=1, email=mock_email, stripe_customer_id="cus_mock")

    # Configurar nueva sesion simulada
    mock_new_session = mocker.Mock()
    mock_new_session.jti = "new_jit"
    mock_new_session.sub = mock_email
    mock_new_session.expires_at = dt.now(timezone.utc) + timedelta(days=1)

    # COnfigurar los mocks
    mocker.patch(
        "services.auth_services.jwt.get_unverified_claims",
        return_value=mock_unverified_payload,
    )

    mocker.patch(
        "services.auth_services.jwt.decode",
        return_value=mock_decoded_payload,
    )

    mocker.patch(
        "services.auth_services.jwt.encode",
        side_effect=[mock_access_token, mock_new_refresh_token],
    )

    # COnfigurar respuestas del repositorio
    mock_repo.get_session_with_jti.return_value = mock_unverified_payload
    mock_repo.get_user_whit_email.return_value = mock_user
    # mock_repo.delete_session.return_value = None
    mock_repo.new_session.return_value = mock_new_session

    # Ejecutar el servicio
    serv = AuthService(mock_repo)
    result = serv.refresh(refresh=mock_refresh_token)

    # Verificaciones
    mock_repo.get_session_with_jti.assert_called_once_with(mock_jti)
    mock_repo.get_user_whit_email.assert_called_once_with(mock_email)
    # mock_repo.delete_session.assert_called_once_with()
    # mock_repo.new_session.assert_called_once_with()

    assert isinstance(result, Token)
    assert result.access_token == mock_access_token
    assert result.refresh_token == mock_new_refresh_token
    assert result.token_type == "bearer"

from models.auth import Sessions
from models.user import Users
from schemas.exceptions import DatabaseError, InvalidToken
from jose import JWTError
from test.conftest import client, auth_headers
from services.auth_services import AuthService, get_auth_serv
from dependencies.auth import get_current_user
from sqlalchemy.exc import SQLAlchemyError
from main import app
from datetime import datetime as dt


def test_login_db_error(mocker, client):
    mock_serv = mocker.Mock(spec=AuthService)

    mock_serv.login.side_effect = DatabaseError(
        error=Exception("Simuled DB Error"), func="AuthService.login"
    )

    app.dependency_overrides[get_auth_serv] = lambda: mock_serv

    response = client.post("/login", json={"email": "test@gmail.com"})

    assert response.status_code == 500
    assert response.json() == {
        "detail": "database error en AuthService.login: Simuled DB Error"
    }

    app.dependency_overrides.clear()


def test_refresh_success(mocker, client):
    mock_serv = mocker.Mock(spec=AuthService)

    mock_serv.refresh.return_value = {
        "access_token": "access_token_moked",
        "token_type": "bearer",
        "refresh_token": "refresh_token_mocked",
    }

    app.dependency_overrides[get_auth_serv] = lambda: mock_serv

    response = client.post("/refresh", json={"refresh": "refresh_token_mocked"})

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "access_token_moked",
        "token_type": "bearer",
        "refresh_token": "refresh_token_mocked",
    }

    app.dependency_overrides.clear()


def test_refresh_db_error(mocker, client):
    mock_serv = mocker.Mock(spec=AuthService)

    mock_serv.refresh.side_effect = DatabaseError(
        error=Exception("Simuled DB Error"), func="AuthService.refresh"
    )

    app.dependency_overrides[get_auth_serv] = lambda: mock_serv

    response = client.post("/refresh", json={"refresh": "refresh_token_mocked"})

    assert response.status_code == 500
    assert response.json() == {
        "detail": "database error en AuthService.refresh: Simuled DB Error"
    }

    app.dependency_overrides.clear()


def test_refresh_jwt_error(mocker, client):
    mock_serv = mocker.Mock(spec=AuthService)

    mock_serv.refresh.side_effect = JWTError()

    app.dependency_overrides[get_auth_serv] = lambda: mock_serv

    response = client.post("/refresh", json={"refresh": "refresh_token_mocked"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Token Not Authorized"}

    app.dependency_overrides.clear()


def test_logout_success(mocker, client):
    mock_serv = mocker.Mock(spec=AuthService)

    mock_serv.logout.return_value = {"detail": "Closed all sessions"}

    mock_user = Users(id=1, email="test@gmail.com", stripe_customer_id=None)

    app.dependency_overrides[get_auth_serv] = lambda: mock_serv
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.post("/logout")

    assert response.status_code == 200
    assert response.json() == {"detail": "Closed all sessions"}

    app.dependency_overrides.clear()


def test_logout_db_error(mocker, client):
    mock_serv = mocker.Mock(spec=AuthService)

    mock_serv.logout.side_effect = DatabaseError(
        error=Exception("Simuled DB Error"), func="AuthService.logout"
    )

    mock_user = Users(id=1, email="test@gmail.com", stripe_customer_id=None)

    app.dependency_overrides[get_auth_serv] = lambda: mock_serv
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.post("/logout")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "database error en AuthService.logout: Simuled DB Error"
    }

    app.dependency_overrides.clear()


def test_get_expired_sessions_success(mocker, client):
    mock_serv = mocker.Mock(spec=AuthService)

    mock_session_expired = Sessions(
        jti="jti_mocked", sub="sub_mocked", is_active=False, expires_at=dt.now()
    )

    mock_serv.get_expired_sessions.side_effect = [mock_session_expired]

    mock_user = Users(id=1, email="test@gmail.com", stripe_customer_id=None)

    app.dependency_overrides[get_auth_serv] = lambda: mock_serv
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.get("/expired")

    assert response.status_code == 200

    item = response.json()

    assert item["jti"] == mock_session_expired.jti
    assert item["sub"] == mock_session_expired.sub
    assert item["is_active"] == mock_session_expired.is_active

    app.dependency_overrides.clear()


def test_get_expired_sessions_db_error(mocker, client):
    mock_serv = mocker.Mock(spec=AuthService)

    mock_serv.get_expired_sessions.side_effect = SQLAlchemyError("Simuled DB Error")

    mock_user = Users(id=1, email="test@gmail.com", stripe_customer_id=None)

    app.dependency_overrides[get_auth_serv] = lambda: mock_serv
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.get("/expired")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "database error en get_expired_sessions: Simuled DB Error"
    }

    app.dependency_overrides.clear()

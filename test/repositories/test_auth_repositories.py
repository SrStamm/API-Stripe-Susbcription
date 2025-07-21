from datetime import datetime as dt
from sqlalchemy.exc import SQLAlchemyError
from models.auth import Sessions
from models.user import Users
from repositories.auth_repositories import AuthRepository
import pytest

from schemas.exceptions import DatabaseError


def test_get_user_by_id(mocker):
    mock_session = mocker.Mock()
    mock_user = Users(id=1, email="test@gmail.com", stripe_customer_id=None)

    mock_session.exec.return_value.first.return_value = mock_user

    repo = AuthRepository(mock_session)

    response = repo.get_user_by_id(1)

    assert response == mock_user


def test_new_session_db_error(mocker):
    mock_session = mocker.Mock()

    mock_session.commit.side_effect = SQLAlchemyError("Simuled DB Error")

    repo = AuthRepository(mock_session)

    with pytest.raises(DatabaseError):
        repo.new_session(jti="jti_mocked", sub="test@gmail.com", expires_at=dt.now())


def test_delete_session_success(mocker):
    mock_session = mocker.Mock()

    mock_session_to_delete = Sessions(
        jti="jti_mocked", sub="test@gmail.com", is_active=True, expires_at=dt.now()
    )
    repo = AuthRepository(mock_session)

    repo.delete_session(mock_session_to_delete)


def test_delete_session_db_error(mocker):
    mock_session = mocker.Mock()

    mock_session_to_delete = Sessions(
        jti="jti_mocked", sub="test@gmail.com", is_active=True, expires_at=dt.now()
    )

    mock_session.commit.side_effect = SQLAlchemyError("Simuled DB Error")

    repo = AuthRepository(mock_session)

    with pytest.raises(DatabaseError):
        repo.delete_session(mock_session_to_delete)


def test_get_session_with_jti_success(mocker):
    mock_session = mocker.Mock()

    mock_session_to_get = Sessions(
        jti="jti_mocked", sub="test@gmail.com", is_active=True, expires_at=dt.now()
    )

    mock_session.exec.return_value.first.return_value = mock_session_to_get

    repo = AuthRepository(mock_session)

    response = repo.get_session_with_jti("jti_mocked")

    assert response == mock_session_to_get


def test_get_active_sessions(mocker):
    mock_session = mocker.Mock()

    mock_session_to_get = Sessions(
        jti="jti_mocked", sub="test@gmail.com", is_active=True, expires_at=dt.now()
    )

    mock_session.exec.return_value.all.return_value = [mock_session_to_get]

    repo = AuthRepository(mock_session)

    response = repo.get_active_sessions("sub_mocked")

    for r in response:
        assert r == mock_session_to_get


def test_get_expired_sessions(mocker):
    mock_session = mocker.Mock()

    mock_session_to_get = Sessions(
        jti="jti_mocked", sub="test@gmail.com", is_active=False, expires_at=dt.now()
    )

    mock_session.exec.return_value.all.return_value = [mock_session_to_get]

    repo = AuthRepository(mock_session)

    response = repo.get_expired_sessions()

    for r in response:
        assert r == mock_session_to_get

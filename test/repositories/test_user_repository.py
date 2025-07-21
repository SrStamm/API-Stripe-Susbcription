from sqlalchemy.exc import SQLAlchemyError
from schemas.exceptions import DatabaseError
from models.user import Users
from repositories.user_repositories import UserRepository
import pytest


def test_get_user_by_email(mocker):
    mock_session = mocker.Mock()

    mock_repo = UserRepository(mock_session)

    mock_session.exec.return_value.first.return_value = Users(
        id=1, email="falso@gmail.com", stripe_customer_id=None
    )

    mock_repo.get_user_by_email("falso@gmail.com")


def test_get_user_by_customer_id(mocker):
    mock_session = mocker.Mock()

    mock_repo = UserRepository(mock_session)

    mock_session.exec.return_value.first.return_value = Users(
        id=1, email="falso@gmail.com", stripe_customer_id="cus_546546"
    )

    mock_repo.get_user_by_customer_id("cus_546546")


def test_get_users_success(mocker):
    mock_session = mocker.Mock()

    user_mocked = Users(id=1, email="falso@gmail.com", stripe_customer_id=None)

    mock_session.exec.return_value.all.return_value = [user_mocked]

    mock_repo = UserRepository(mock_session)

    response = mock_repo.get_users()

    for r in response:
        assert r == user_mocked


def test_create(mocker):
    mock_session = mocker.Mock()

    mock_repo = UserRepository(mock_session)

    mock_repo.create("test@gmail.com")


def test_create_error(mocker):
    mock_session = mocker.Mock()

    mock_repo = UserRepository(mock_session)

    mock_session.commit.side_effect = SQLAlchemyError("ERROR INTERNO")
    with pytest.raises(DatabaseError):
        mock_repo.create("test@gmail.com")


def test_update(mocker):
    mock_session = mocker.Mock()

    mock_user = mocker.Mock(spec=Users)
    mock_user.id = 1
    mock_user.email = "test@gmail.com"
    mock_user.stripe_customer_id = None

    mock_session.exec.return_value.first.return_value = mock_user

    repo = UserRepository(mock_session)

    repo.update(id=1, stripe_id="cus_546546")

    assert mock_user.stripe_customer_id == "cus_546546"

    mock_session.commit.assert_called_once()

    mock_session.refresh.assert_not_called()


def test_update_error(mocker):
    mock_session = mocker.Mock()

    mock_user = mocker.Mock(spec=Users)
    mock_user.id = 1
    mock_user.email = "test@gmail.com"
    mock_user.stripe_customer_id = None

    mock_session.exec.return_value.first.return_value = mock_user

    mock_session.commit.side_effect = SQLAlchemyError("EROR INTERNO")

    repo = UserRepository(mock_session)

    with pytest.raises(DatabaseError):
        repo.update(id=1, stripe_id="cus_546546")

    mock_session.commit.assert_called_once()


def test_delete(mocker):
    mock_session = mocker.Mock()

    mock_user = mocker.Mock(spec=Users)
    mock_user.id = 1
    mock_user.email = "test@gmail.com"
    mock_user.stripe_customer_id = "cus_546546"

    mock_session.exec.return_value.first.return_value = mock_user

    mock_session.commit.side_effect = SQLAlchemyError("EROR INTERNO")

    repo = UserRepository(mock_session)

    with pytest.raises(DatabaseError):
        repo.delete(customer_id="cus_546546")


def test_delete_error(mocker):
    mock_session = mocker.Mock()

    mock_user = mocker.Mock(spec=Users)
    mock_user.id = 1
    mock_user.email = "test@gmail.com"
    mock_user.stripe_customer_id = "cus_546546"

    mock_session.exec.return_value.first.return_value = mock_user

    repo = UserRepository(mock_session)

    repo.delete(customer_id="cus_546546")

    assert mock_user.stripe_customer_id == "cus_546546"

    mock_session.delete.assert_called_once()

    mock_session.commit.assert_called_once()

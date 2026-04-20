import pytest

from models.user import Users
from schemas.exceptions import DatabaseError
from tasks.customer import customer_created, customer_deleted


@pytest.fixture
def mock_repos(mocker):
    """Mock repositories for task tests."""
    from unittest.mock import Mock

    mock_session = Mock()
    mock_repo = Mock()

    mocker.patch("db.session.get_session", return_value=iter([mock_session]))
    mocker.patch(
        "helpers.context.UserRepository",
        return_value=mock_repo,
    )

    return mock_repo


def test_customer_created_success(mock_repos):
    """Test successful customer.created."""
    mock_repo = mock_repos

    mock_repo.get_user_by_customer_id.return_value = None
    mock_repo.create.return_value = Users(
        id=1, email="test@gmail.com", stripe_customer_id="cus_mocked_id"
    )

    payload = {"id": "cus_id", "email": "test@gmail.com"}

    customer_created(payload)

    mock_repo.get_user_by_customer_id.assert_called_once_with("cus_id")
    mock_repo.create.assert_called_once_with(email="test@gmail.com")
    mock_repo.update.assert_called_once_with(id=1, stripe_id="cus_id")


def test_customer_created_existing_user(mock_repos):
    """Test customer.created with existing user."""
    mock_repo = mock_repos

    mock_repo.get_user_by_customer_id.return_value = Users(
        id=1, email="test@gmail.com", stripe_customer_id="cus_id"
    )

    payload = {"id": "cus_id", "email": "test@gmail.com"}

    customer_created(payload)

    mock_repo.get_user_by_customer_id.assert_called_once_with("cus_id")
    mock_repo.create.assert_not_called()


def test_customer_created_db_error(mock_repos):
    """Test customer.created with DB error."""
    mock_repo = mock_repos

    from sqlalchemy.exc import SQLAlchemyError

    mock_repo.get_user_by_customer_id.side_effect = DatabaseError(
        error=SQLAlchemyError("db error"), func="get_user_by_customer_id"
    )

    payload = {"id": "cus_id", "email": "test@gmail.com"}

    with pytest.raises(DatabaseError):
        customer_created(payload)


def test_customer_created_unexpected_error(mock_repos):
    """Test customer.created with unexpected error."""
    mock_repo = mock_repos

    mock_repo.get_user_by_customer_id.side_effect = Exception()

    payload = {"id": "cus_id", "email": "test@gmail.com"}

    with pytest.raises(Exception):
        customer_created(payload)


def test_customer_deleted_success(mock_repos):
    """Test successful customer.deleted."""
    mock_repo = mock_repos

    payload = {"id": "cus_id"}

    customer_deleted(payload)

    mock_repo.delete.assert_called_once_with("cus_id")


def test_customer_deleted_db_error(mock_repos):
    """Test customer.deleted with DB error."""
    mock_repo = mock_repos

    mock_repo.delete.side_effect = DatabaseError(
        error=Exception(), func="UserRepository.delete"
    )

    payload = {"id": "cus_id"}

    with pytest.raises(DatabaseError):
        customer_deleted(payload)


def test_customer_deleted_unexpected_error(mock_repos):
    """Test customer.deleted with unexpected error."""
    mock_repo = mock_repos

    mock_repo.delete.side_effect = Exception()

    payload = {"id": "cus_id"}

    with pytest.raises(Exception):
        customer_deleted(payload)
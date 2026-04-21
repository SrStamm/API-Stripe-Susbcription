"""Tests for CustomerService webhook handlers."""
import pytest

from models.user import Users
from services.customer_service import (
    CustomerService,
    CustomerCreatedInfo,
    CustomerDeletedInfo,
)


@pytest.fixture
def mock_service(mocker):
    """Create CustomerService with mocked repository."""
    user_repo = mocker.Mock()
    service = CustomerService(user_repo=user_repo)

    return {
        "service": service,
        "user_repo": user_repo,
    }


class TestHandleCustomerCreated:
    """Tests for handle_customer_created method."""

    def test_new_user(self, mock_service):
        """Test creating new user when not exists."""
        service = mock_service["service"]
        user_repo = mock_service["user_repo"]

        # Mock user NOT found
        user_repo.get_user_by_customer_id.return_value = None

        # Mock created user
        user_repo.create.return_value = Users(
            id=1, email="test@example.com", stripe_customer_id="cus_test"
        )

        info = CustomerCreatedInfo(
            stripe_id="cus_test",
            email="test@example.com",
        )

        service.handle_customer_created(info)

        user_repo.get_user_by_customer_id.assert_called_once_with("cus_test")
        user_repo.create.assert_called_once_with(email="test@example.com")
        user_repo.update.assert_called_once_with(id=1, stripe_id="cus_test")

    def test_existing_user(self, mock_service):
        """Test handling when user already exists."""
        service = mock_service["service"]
        user_repo = mock_service["user_repo"]

        # Mock user found
        user_repo.get_user_by_customer_id.return_value = Users(
            id=1, email="test@example.com", stripe_customer_id="cus_test"
        )

        info = CustomerCreatedInfo(
            stripe_id="cus_test",
            email="test@example.com",
        )

        service.handle_customer_created(info)

        user_repo.get_user_by_customer_id.assert_called_once_with("cus_test")
        user_repo.create.assert_not_called()
        user_repo.update.assert_not_called()


class TestHandleCustomerDeleted:
    """Tests for handle_customer_deleted method."""

    def test_success(self, mock_service):
        """Test successful customer deletion."""
        service = mock_service["service"]
        user_repo = mock_service["user_repo"]

        info = CustomerDeletedInfo(stripe_id="cus_test")

        service.handle_customer_deleted(info)

        user_repo.delete.assert_called_once_with("cus_test")
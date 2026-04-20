from datetime import datetime
from unittest.mock import Mock

import pytest

from models.plan import Plans
from models.user import Users
from schemas.enums import SubscriptionStatus
from schemas.exceptions import DatabaseError
from tasks.subscriptions import (
    customer_sub_basic,
    customer_subscription_created,
    customer_subscription_deleted,
    customer_subscription_paused,
    customer_subscription_updated,
)


@pytest.fixture
def mock_repos(mocker):
    """Mock repositories for task tests."""
    mock_session = mocker.Mock()
    mock_sub_repo = mocker.Mock()
    mock_plan_repo = mocker.Mock()
    mock_user_repo = mocker.Mock()

    mocker.patch("db.session.get_session", return_value=iter([mock_session]))
    mocker.patch(
        "helpers.context.SubscriptionRepository",
        return_value=mock_sub_repo,
    )
    mocker.patch(
        "helpers.context.UserRepository",
        return_value=mock_user_repo,
    )
    mocker.patch(
        "helpers.context.PlanRepository",
        return_value=mock_plan_repo,
    )

    return {
        "session": mock_session,
        "sub_repo": mock_sub_repo,
        "plan_repo": mock_plan_repo,
        "user_repo": mock_user_repo,
    }


def test_customer_sub_basic_success(mock_repos):
    """Test successful customer_sub_basic."""
    user_repo = mock_repos["user_repo"]
    plan_repo = mock_repos["plan_repo"]
    sub_repo = mock_repos["sub_repo"]

    user_repo.get_user_by_customer_id.return_value = Users(
        id=1, email="test@gmail.com", stripe_customer_id=None
    )
    plan_repo.get_plan_by_tier.return_value = Plans(
        id=1,
        stripe_price_id="price_mocked",
        name="free",
        description=None,
        price_cents=0,
        interval="month",
    )

    payload = {"id": "cus_mock_test"}

    customer_sub_basic(payload)

    user_repo.get_user_by_customer_id.assert_called_once_with("cus_mock_test")
    sub_repo.create.assert_called_once()
    sub_repo.update_for_user.assert_called_once()


def test_customer_sub_basic_user_error(mock_repos):
    """Test customer_sub_basic when user not found."""
    user_repo = mock_repos["user_repo"]

    user_repo.get_user_by_customer_id.return_value = None

    payload = {"id": "cus_mock_test"}

    with pytest.raises(Exception):
        customer_sub_basic(payload)


def test_customer_sub_basic_plan_error(mock_repos):
    """Test customer_sub_basic when plan not found."""
    user_repo = mock_repos["user_repo"]
    plan_repo = mock_repos["plan_repo"]

    user_repo.get_user_by_customer_id.return_value = Users(
        id=1, email="test@gmail.com", stripe_customer_id=None
    )
    plan_repo.get_plan_by_tier.return_value = None

    payload = {"id": "cus_mock_test"}

    with pytest.raises(Exception):
        customer_sub_basic(payload)


def test_customer_sub_basic_db_error(mock_repos):
    """Test customer_sub_basic with DB error."""
    user_repo = mock_repos["user_repo"]

    user_repo.get_user_by_customer_id.side_effect = DatabaseError(
        error="DB error", func="get_user_by_customer_id"
    )

    payload = {"id": "cus_mock_test"}

    with pytest.raises(DatabaseError):
        customer_sub_basic(payload)


def test_customer_subscription_created_success(mock_repos):
    """Test successful customer.subscription.created."""
    sub_repo = mock_repos["sub_repo"]

    payload = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "active",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    customer_subscription_created(payload)

    sub_repo.update_for_user.assert_called_once_with(
        sub_id="sub_mock_test",
        customer_id="cus_mock_test",
        status=SubscriptionStatus.trialing,
        current_period_end=datetime.fromtimestamp(123456789),
        is_active=True,
    )


def test_customer_subscription_created_db_error(mock_repos):
    """Test customer.subscription.created with DB error."""
    sub_repo = mock_repos["sub_repo"]
    sub_repo.update_for_user.side_effect = DatabaseError(
        error="DB error", func="update_for_user"
    )

    payload = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "active",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    with pytest.raises(DatabaseError):
        customer_subscription_created(payload)


def test_customer_subscription_created_unexpected_error(mock_repos):
    """Test customer.subscription.created with unexpected error."""
    sub_repo = mock_repos["sub_repo"]
    sub_repo.update_for_user.side_effect = Exception("Unexpected")

    payload = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "active",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    with pytest.raises(Exception):
        customer_subscription_created(payload)


def test_customer_subscription_updated_success(mock_repos):
    """Test successful customer.subscription.updated."""
    sub_repo = mock_repos["sub_repo"]

    payload = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "active",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    customer_subscription_updated(payload)

    sub_repo.update_for_user.assert_called_once_with(
        sub_id="sub_mock_test",
        customer_id="cus_mock_test",
        status=SubscriptionStatus.trialing,
        current_period_end=datetime.fromtimestamp(123456789),
        is_active=True,
    )


def test_customer_subscription_updated_inactive(mock_repos):
    """Test customer.subscription.updated with inactive status."""
    sub_repo = mock_repos["sub_repo"]

    payload = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "incomplete",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    customer_subscription_updated(payload)

    sub_repo.update_for_user.assert_called_once_with(
        sub_id="sub_mock_test",
        customer_id="cus_mock_test",
        status=SubscriptionStatus.incomplete,
        current_period_end=datetime.fromtimestamp(123456789),
        is_active=False,
    )


def test_customer_subscription_updated_unexpected_error(mock_repos):
    """Test customer.subscription.updated with unexpected error."""
    sub_repo = mock_repos["sub_repo"]
    sub_repo.update_for_user.side_effect = Exception("Unexpected")

    payload = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "active",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    with pytest.raises(Exception):
        customer_subscription_updated(payload)


def test_customer_subscription_updated_db_error(mock_repos):
    """Test customer.subscription.updated with DB error."""
    sub_repo = mock_repos["sub_repo"]
    sub_repo.update_for_user.side_effect = DatabaseError(
        error="DB error", func="update_for_user"
    )

    payload = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "active",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    with pytest.raises(DatabaseError):
        customer_subscription_updated(payload)


def test_customer_subscription_deleted_success(mock_repos):
    """Test successful customer.subscription.deleted."""
    sub_repo = mock_repos["sub_repo"]

    payload = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "canceled",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    customer_subscription_deleted(payload)

    sub_repo.cancel.assert_called_once_with(
        sub_id="sub_mock_test",
        customer_id="cus_mock_test",
        status=SubscriptionStatus.from_stripe("canceled"),
        current_period_end=datetime.fromtimestamp(123456789),
    )


def test_customer_subscription_deleted_db_error(mock_repos):
    """Test customer.subscription.deleted with DB error."""
    sub_repo = mock_repos["sub_repo"]
    sub_repo.cancel.side_effect = DatabaseError(
        error="DB error", func="cancel"
    )

    payload = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "canceled",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    with pytest.raises(DatabaseError):
        customer_subscription_deleted(payload)


def test_customer_subscription_deleted_unexpected_error(mock_repos):
    """Test customer.subscription.deleted with unexpected error."""
    sub_repo = mock_repos["sub_repo"]
    sub_repo.cancel.side_effect = Exception("Unexpected")

    payload = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "canceled",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    with pytest.raises(Exception):
        customer_subscription_deleted(payload)


def test_customer_subscription_paused_success(mock_repos):
    """Test successful customer.subscription.paused."""
    sub_repo = mock_repos["sub_repo"]

    payload = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "paused",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    customer_subscription_paused(payload)

    sub_repo.update_for_user.assert_called_once_with(
        sub_id="sub_mock_test",
        customer_id="cus_mock_test",
        status=SubscriptionStatus.from_stripe("paused"),
        current_period_end=None,
        is_active=False,
    )


def test_customer_subscription_paused_db_error(mock_repos):
    """Test customer.subscription.paused with DB error."""
    sub_repo = mock_repos["sub_repo"]
    sub_repo.update_for_user.side_effect = DatabaseError(
        error="DB error", func="update_for_user"
    )

    payload = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "paused",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    with pytest.raises(DatabaseError):
        customer_subscription_paused(payload)


def test_customer_subscription_paused_unexpected_error(mock_repos):
    """Test customer.subscription.paused with unexpected error."""
    sub_repo = mock_repos["sub_repo"]
    sub_repo.update_for_user.side_effect = Exception("Unexpected")

    payload = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "paused",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    with pytest.raises(Exception):
        customer_subscription_paused(payload)
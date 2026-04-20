from datetime import datetime

import pytest

from schemas.enums import SubscriptionStatus
from tasks.invoice import invoice_paid, invoice_payment_failed


@pytest.fixture
def mock_repos(mocker):
    """Mock repositories for task tests."""
    mock_session = mocker.Mock()
    mock_repo = mocker.Mock()

    mocker.patch("db.session.get_session", return_value=iter([mock_session]))
    mocker.patch(
        "helpers.context.SubscriptionRepository",
        return_value=mock_repo,
    )
    mocker.patch("helpers.context.UserRepository", return_value=mocker.Mock())
    mocker.patch("helpers.context.PlanRepository", return_value=mocker.Mock())

    return mock_repo


def test_invoice_paid_success(mock_repos):
    """Test successful invoice.paid."""
    mock_repo = mock_repos
    mock_repo.get_subscription_for_user.return_value = {"id": "user_test"}

    payload = {
        "billing_reason": "subscription_create",
        "lines": {
            "data": [
                {
                    "parent": {
                        "subscription_item_details": {"subscription": "sub_test"},
                    },
                    "period": {"end": 123456789},
                }
            ],
        },
        "customer": "cus_test",
        "status": "paid",
    }

    invoice_paid(payload)

    mock_repo.get_subscription_for_user.assert_called_once_with(
        sub_id="sub_test", customer_id="cus_test"
    )
    mock_repo.update_for_user.assert_called_once_with(
        sub_id="sub_test",
        customer_id="cus_test",
        status=SubscriptionStatus.paid,
        current_period_end=datetime.fromtimestamp(123456789),
        is_active=True,
    )


def test_invoice_paid_not_relationated():
    """Test invoice.paid with non-subscription billing reason."""
    payload = {}
    invoice_paid(payload)  # Should return None, not raise


def test_invoice_paid_not_subscription():
    """Test invoice.paid with subscription_create but no lines."""
    payload = {"billing_reason": "subscription_create"}

    with pytest.raises(Exception):
        invoice_paid(payload)


def test_not_subs_detail(mock_repos):
    """Test invoice.paid with missing subscription details."""
    mock_repo = mock_repos

    payload = {
        "billing_reason": "subscription_create",
        "lines": {
            "data": [{"parent": {"det": "asad"}}],
        },
    }

    with pytest.raises(Exception):
        invoice_paid(payload)


def test_not_sub_id(mock_repos):
    """Test invoice.paid with missing subscription ID."""
    mock_repo = mock_repos

    payload = {
        "billing_reason": "subscription_create",
        "lines": {
            "data": [
                {
                    "parent": {"subscription_item_details": {}},
                }
            ],
        },
        "customer": None,
    }

    with pytest.raises(Exception):
        invoice_paid(payload)


def test_not_sub_error(mock_repos):
    """Test invoice.paid when subscription not found."""
    mock_repo = mock_repos
    mock_repo.get_subscription_for_user.return_value = None

    payload = {
        "billing_reason": "subscription_create",
        "lines": {
            "data": [
                {
                    "parent": {
                        "subscription_item_details": {"subscription": "sub_test"},
                    },
                    "period": {"end": 123456789},
                }
            ],
        },
        "customer": "cus_test",
        "status": "paid",
    }

    with pytest.raises(Exception):
        invoice_paid(payload)

    mock_repo.get_subscription_for_user.assert_called_once_with(
        sub_id="sub_test", customer_id="cus_test"
    )


def test_invoice_payment_failed_success(mock_repos):
    """Test successful invoice.payment_failed."""
    mock_repo = mock_repos
    mock_repo.get_subscription_for_user.return_value = {
        "id": "user_test",
        "stripe_subscription_id": "sub_test",
    }

    payload = {
        "lines": {
            "data": [
                {
                    "parent": {
                        "subscription_item_details": {"subscription": "sub_test"},
                    },
                    "period": {"end": 123456789},
                }
            ],
        },
        "customer": "cus_test",
        "status": "failed",
    }

    invoice_payment_failed(payload)

    mock_repo.get_subscription_for_user.assert_called_once_with(
        sub_id="sub_test",
        customer_id="cus_test",
    )
    mock_repo.update_for_user.assert_called_once_with(
        sub_id="sub_test",
        customer_id="cus_test",
        status=SubscriptionStatus.past_due,
        current_period_end=datetime.fromtimestamp(123456789),
        is_active=False,
    )


def test_invoice_payment_failed_bad_structure():
    """Test invoice.payment_failed with bad payload."""
    payload = {}

    with pytest.raises(Exception):
        invoice_payment_failed(payload)


def test_invoice_payment_failed_not_details(mock_repos):
    """Test invoice.payment_failed with missing details."""
    mock_repo = mock_repos

    payload = {
        "lines": {
            "data": [{"parent": {}}],
        },
    }

    with pytest.raises(Exception):
        invoice_payment_failed(payload)


def test_invoice_payment_failed_not_suscription(mock_repos):
    """Test invoice.payment_failed when subscription not found."""
    mock_repo = mock_repos
    mock_repo.get_subscription_for_user.return_value = None

    payload = {
        "lines": {
            "data": [
                {
                    "parent": {
                        "subscription_item_details": {"subscription": "sub_test"},
                    },
                    "period": {"end": 123456789},
                }
            ],
        },
        "customer": "cus_test",
        "status": "failed",
    }

    with pytest.raises(Exception):
        invoice_payment_failed(payload)

    mock_repo.get_subscription_for_user.assert_called_once_with(
        sub_id="sub_test",
        customer_id="cus_test",
    )
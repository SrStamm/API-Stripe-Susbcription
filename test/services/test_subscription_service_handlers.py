"""Tests for SubscriptionService webhook handlers."""
import pytest
from datetime import datetime

from models.user import Users
from models.plan import Plans
from schemas.enums import SubscriptionStatus, SubscriptionTier
from services.subscription_service import (
    SubscriptionService,
    InvoicePaidInfo,
    SubscriptionCreatedInfo,
    SubscriptionUpdatedInfo,
    SubscriptionDeletedInfo,
    SubscriptionPausedInfo,
)


@pytest.fixture
def mock_service(mocker):
    """Create SubscriptionService with mocked repositories."""
    sub_repo = mocker.Mock()
    user_repo = mocker.Mock()
    plan_repo = mocker.Mock()

    service = SubscriptionService(
        repo=sub_repo, user_repo=user_repo, plan_repo=plan_repo
    )

    return {
        "service": service,
        "sub_repo": sub_repo,
        "user_repo": user_repo,
        "plan_repo": plan_repo,
    }


class TestHandleInvoicePaid:
    """Tests for handle_invoice_paid method."""

    def test_success(self, mock_service):
        """Test successful invoice.paid handling."""
        service = mock_service["service"]
        sub_repo = mock_service["sub_repo"]

        # Mock subscription found
        sub_repo.get_subscription_for_user.return_value = {"id": 1}

        info = InvoicePaidInfo(
            subscription_id="sub_test",
            customer_id="cus_test",
            current_period_end=datetime.now(),
            status="paid",
        )

        service.handle_invoice_paid(info)

        sub_repo.update_for_user.assert_called_once()
        call_kwargs = sub_repo.update_for_user.call_args.kwargs
        assert call_kwargs["sub_id"] == "sub_test"
        assert call_kwargs["customer_id"] == "cus_test"
        assert call_kwargs["is_active"] is True

    def test_subscription_not_found(self, mock_service):
        """Test handling when subscription not found."""
        service = mock_service["service"]
        sub_repo = mock_service["sub_repo"]

        # Mock subscription NOT found
        sub_repo.get_subscription_for_user.return_value = None

        info = InvoicePaidInfo(
            subscription_id="sub_not_found",
            customer_id="cus_test",
            current_period_end=datetime.now(),
            status="paid",
        )

        with pytest.raises(Exception, match="Subscription sub_not_found not found"):
            service.handle_invoice_paid(info)


class TestHandleInvoicePaymentFailed:
    """Tests for handle_invoice_payment_failed method."""

    def test_success(self, mock_service):
        """Test successful invoice.payment_failed handling."""
        service = mock_service["service"]
        sub_repo = mock_service["sub_repo"]

        sub_repo.get_subscription_for_user.return_value = {"id": 1}

        info = InvoicePaidInfo(
            subscription_id="sub_test",
            customer_id="cus_test",
            current_period_end=datetime.now(),
            status="failed",
        )

        service.handle_invoice_payment_failed(info)

        sub_repo.update_for_user.assert_called_once()
        call_kwargs = sub_repo.update_for_user.call_args.kwargs
        assert call_kwargs["status"] == SubscriptionStatus.past_due
        assert call_kwargs["is_active"] is False


class TestHandleCustomerSubscriptionCreated:
    """Tests for handle_customer_subscription_created method."""

    def test_success(self, mock_service):
        """Test successful customer.subscription.created handling."""
        service = mock_service["service"]
        sub_repo = mock_service["sub_repo"]

        info = SubscriptionCreatedInfo(
            subscription_id="sub_test",
            customer_id="cus_test",
            current_period_end=datetime.now(),
            status="active",
        )

        service.handle_customer_subscription_created(info)

        sub_repo.update_for_user.assert_called_once()
        call_kwargs = sub_repo.update_for_user.call_args.kwargs
        assert call_kwargs["sub_id"] == "sub_test"
        assert call_kwargs["is_active"] is True


class TestHandleCustomerSubscriptionUpdated:
    """Tests for handle_customer_subscription_updated method."""

    def test_active_status(self, mock_service):
        """Test handling with active status."""
        service = mock_service["service"]
        sub_repo = mock_service["sub_repo"]

        info = SubscriptionUpdatedInfo(
            subscription_id="sub_test",
            customer_id="cus_test",
            current_period_end=datetime.now(),
            status="active",
            is_active=True,
        )

        service.handle_customer_subscription_updated(info)

        sub_repo.update_for_user.assert_called_once()
        call_kwargs = sub_repo.update_for_user.call_args.kwargs
        assert call_kwargs["is_active"] is True

    def test_inactive_status(self, mock_service):
        """Test handling with inactive status."""
        service = mock_service["service"]
        sub_repo = mock_service["sub_repo"]

        info = SubscriptionUpdatedInfo(
            subscription_id="sub_test",
            customer_id="cus_test",
            current_period_end=datetime.now(),
            status="past_due",
            is_active=False,
        )

        service.handle_customer_subscription_updated(info)

        call_kwargs = sub_repo.update_for_user.call_args.kwargs
        assert call_kwargs["is_active"] is False


class TestHandleCustomerSubscriptionDeleted:
    """Tests for handle_customer_subscription_deleted method."""

    def test_success(self, mock_service):
        """Test successful customer.subscription.deleted handling."""
        service = mock_service["service"]
        sub_repo = mock_service["sub_repo"]

        info = SubscriptionDeletedInfo(
            subscription_id="sub_test",
            customer_id="cus_test",
            current_period_end=datetime.now(),
            status="canceled",
        )

        service.handle_customer_subscription_deleted(info)

        sub_repo.cancel.assert_called_once()
        call_kwargs = sub_repo.cancel.call_args.kwargs
        assert call_kwargs["sub_id"] == "sub_test"
        assert call_kwargs["customer_id"] == "cus_test"


class TestHandleCustomerSubscriptionPaused:
    """Tests for handle_customer_subscription_paused method."""

    def test_success(self, mock_service):
        """Test successful customer.subscription.paused handling."""
        service = mock_service["service"]
        sub_repo = mock_service["sub_repo"]

        info = SubscriptionPausedInfo(
            subscription_id="sub_test",
            customer_id="cus_test",
            status="paused",
        )

        service.handle_customer_subscription_paused(info)

        sub_repo.update_for_user.assert_called_once()
        call_kwargs = sub_repo.update_for_user.call_args.kwargs
        assert call_kwargs["sub_id"] == "sub_test"
        assert call_kwargs["current_period_end"] is None
        assert call_kwargs["is_active"] is False


class TestHandleCustomerSubBasic:
    """Tests for handle_customer_sub_basic method."""

    def test_success(self, mock_service):
        """Test successful customer_sub_basic handling."""
        service = mock_service["service"]
        user_repo = mock_service["user_repo"]
        plan_repo = mock_service["plan_repo"]
        sub_repo = mock_service["sub_repo"]

        # Mock user found
        user_repo.get_user_by_customer_id.return_value = Users(
            id=1, email="test@example.com", stripe_customer_id="cus_test"
        )

        # Mock plan found
        plan_repo.get_plan_by_tier.return_value = Plans(
            id=1,
            stripe_price_id="price_free",
            name="free",
            description="Free tier",
            price_cents=0,
            interval="month",
        )

        service.handle_customer_sub_basic("cus_test")

        user_repo.get_user_by_customer_id.assert_called_once_with("cus_test")
        plan_repo.get_plan_by_tier.assert_called_once_with(tier=SubscriptionTier.free)
        sub_repo.create.assert_called_once()
        sub_repo.update_for_user.assert_called_once()

    def test_user_not_found(self, mock_service):
        """Test handling when user not found."""
        service = mock_service["service"]
        user_repo = mock_service["user_repo"]

        user_repo.get_user_by_customer_id.return_value = None

        with pytest.raises(Exception, match="User with stripe_id"):
            service.handle_customer_sub_basic("cus_not_found")

    def test_plan_not_found(self, mock_service):
        """Test handling when plan not found."""
        service = mock_service["service"]
        user_repo = mock_service["user_repo"]
        plan_repo = mock_service["plan_repo"]

        user_repo.get_user_by_customer_id.return_value = Users(
            id=1, email="test@example.com", stripe_customer_id="cus_test"
        )
        plan_repo.get_plan_by_tier.return_value = None

        with pytest.raises(Exception, match="Plan with tier FREE not found"):
            service.handle_customer_sub_basic("cus_test")
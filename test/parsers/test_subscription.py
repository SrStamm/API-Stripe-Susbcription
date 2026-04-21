import pytest

from datetime import datetime
from parsers.subscription import (
    SubscriptionPayload,
    SubscriptionItem,
    SubscriptionItems,
    parse_customer_subscription_created,
    parse_customer_subscription_updated,
    parse_customer_subscription_deleted,
    parse_customer_subscription_paused,
)


class TestSubscriptionPayload:
    """Test SubscriptionPayload schema validation."""

    def test_valid_full_payload(self):
        """Test SubscriptionPayload with all fields."""
        payload = {
            "id": "sub_test",
            "customer": "cus_test",
            "status": "active",
            "items": {
                "data": [{"current_period_end": 1234567890}]
            },
        }

        result = SubscriptionPayload(**payload)

        assert result.id == "sub_test"
        assert result.customer == "cus_test"
        assert result.status == "active"
        assert len(result.items.data) == 1

    def test_payload_with_minimal_fields(self):
        """Test SubscriptionPayload with minimal required fields."""
        payload = {
            "id": "sub_test",
        }

        result = SubscriptionPayload(**payload)

        assert result.id == "sub_test"
        assert result.customer is None
        assert result.status is None
        assert result.items is None


class TestParseCustomerSubscriptionCreated:
    """Test parse_customer_subscription_created function."""

    def test_valid_payload(self):
        """Test parsing customer.subscription.created."""
        payload = SubscriptionPayload(
            id="sub_test",
            customer="cus_test",
            status="active",
            items=SubscriptionItems(
                data=[SubscriptionItem(current_period_end=1234567890)]
            ),
        )

        result = parse_customer_subscription_created(payload)

        assert result.subscription_id == "sub_test"
        assert result.customer_id == "cus_test"
        assert result.current_period_end == datetime.fromtimestamp(1234567890)
        assert result.status == "active"

    def test_empty_items_raises_error(self):
        """Test that empty items raises ValueError."""
        payload = SubscriptionPayload(
            id="sub_test",
            customer="cus_test",
            status="active",
            items=SubscriptionItems(data=[]),
        )

        with pytest.raises(ValueError, match="No subscription items found"):
            parse_customer_subscription_created(payload)


class TestParseCustomerSubscriptionUpdated:
    """Test parse_customer_subscription_updated function."""

    def test_active_status(self):
        """Test parsing with active status."""
        payload = SubscriptionPayload(
            id="sub_test",
            customer="cus_test",
            status="active",
            items=SubscriptionItems(
                data=[SubscriptionItem(current_period_end=1234567890)]
            ),
        )

        result = parse_customer_subscription_updated(payload)

        assert result.subscription_id == "sub_test"
        assert result.is_active is True

    def test_inactive_status(self):
        """Test parsing with inactive status (paused)."""
        payload = SubscriptionPayload(
            id="sub_test",
            customer="cus_test",
            status="paused",
            items=SubscriptionItems(
                data=[SubscriptionItem(current_period_end=1234567890)]
            ),
        )

        result = parse_customer_subscription_updated(payload)

        assert result.subscription_id == "sub_test"
        assert result.is_active is False

    def test_incomplete_status(self):
        """Test parsing with incomplete status."""
        payload = SubscriptionPayload(
            id="sub_test",
            customer="cus_test",
            status="incomplete",
            items=SubscriptionItems(
                data=[SubscriptionItem(current_period_end=1234567890)]
            ),
        )

        result = parse_customer_subscription_updated(payload)

        assert result.subscription_id == "sub_test"
        assert result.is_active is False


class TestParseCustomerSubscriptionDeleted:
    """Test parse_customer_subscription_deleted function."""

    def test_valid_payload(self):
        """Test parsing customer.subscription.deleted."""
        payload = SubscriptionPayload(
            id="sub_test",
            customer="cus_test",
            status="canceled",
            items=SubscriptionItems(
                data=[SubscriptionItem(current_period_end=1234567890)]
            ),
        )

        result = parse_customer_subscription_deleted(payload)

        assert result.subscription_id == "sub_test"
        assert result.customer_id == "cus_test"
        assert result.current_period_end == datetime.fromtimestamp(1234567890)
        assert result.status == "canceled"


class TestParseCustomerSubscriptionPaused:
    """Test parse_customer_subscription_paused function."""

    def test_valid_payload(self):
        """Test parsing customer.subscription.paused."""
        payload = SubscriptionPayload(
            id="sub_test",
            customer="cus_test",
            status="paused",
            items=SubscriptionItems(data=[]),
        )

        result = parse_customer_subscription_paused(payload)

        assert result.subscription_id == "sub_test"
        assert result.customer_id == "cus_test"
        assert result.status == "paused"
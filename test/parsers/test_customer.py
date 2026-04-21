import pytest

from parsers.customer import (
    CustomerPayload,
    parse_customer_created,
    parse_customer_deleted,
)


class TestCustomerPayload:
    """Test CustomerPayload schema validation."""

    def test_valid_full_payload(self):
        """Test CustomerPayload with all fields."""
        payload = {
            "id": "cus_test",
            "email": "test@example.com",
        }

        result = CustomerPayload(**payload)

        assert result.id == "cus_test"
        assert result.email == "test@example.com"

    def test_payload_with_minimal_fields(self):
        """Test CustomerPayload with only id."""
        payload = {
            "id": "cus_test",
        }

        result = CustomerPayload(**payload)

        assert result.id == "cus_test"
        assert result.email is None


class TestParseCustomerCreated:
    """Test parse_customer_created function."""

    def test_valid_payload(self):
        """Test parsing customer.created."""
        payload = CustomerPayload(
            id="cus_test",
            email="test@example.com",
        )

        result = parse_customer_created(payload)

        assert result.stripe_id == "cus_test"
        assert result.email == "test@example.com"


class TestParseCustomerDeleted:
    """Test parse_customer_deleted function."""

    def test_valid_payload(self):
        """Test parsing customer.deleted."""
        payload = CustomerPayload(
            id="cus_test",
        )

        result = parse_customer_deleted(payload)

        assert result.stripe_id == "cus_test"
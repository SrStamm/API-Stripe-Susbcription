import pytest

from datetime import datetime
from parsers.invoice import (
    InvoicePayload,
    InvoiceLine,
    InvoiceLinePeriod,
    InvoiceLineParent,
    InvoiceLineParentSubscriptionItemDetails,
    InvoiceLines,
    parse_invoice_paid,
    parse_invoice_payment_failed,
)


class TestInvoicePayload:
    """Test InvoicePayload schema validation."""

    def test_valid_full_payload(self):
        """Test InvoicePayload with all fields."""
        payload = {
            "customer": "cus_test",
            "status": "paid",
            "billing_reason": "subscription_create",
            "lines": {
                "data": [
                    {
                        "period": {"end": 1234567890},
                        "parent": {
                            "subscription_item_details": {
                                "subscription": "sub_test"
                            }
                        },
                    }
                ]
            },
        }

        result = InvoicePayload(**payload)

        assert result.customer == "cus_test"
        assert result.status == "paid"
        assert result.billing_reason == "subscription_create"
        assert len(result.lines.data) == 1

    def test_payload_with_minimal_fields(self):
        """Test InvoicePayload with minimal required fields."""
        payload = {
            "customer": "cus_test",
            "status": "paid",
        }

        result = InvoicePayload(**payload)

        assert result.customer == "cus_test"
        assert result.status == "paid"
        assert result.lines is None
        assert result.billing_reason is None


class TestParseInvoicePaid:
    """Test parse_invoice_paid function."""

    def test_valid_subscription_create(self):
        """Test parsing invoice.paid with subscription_create billing reason."""
        payload = InvoicePayload(
            customer="cus_test",
            status="paid",
            billing_reason="subscription_create",
            lines=InvoiceLines(
                data=[
                    InvoiceLine(
                        period=InvoiceLinePeriod(end=1234567890),
                        parent=InvoiceLineParent(
                            subscription_item_details=InvoiceLineParentSubscriptionItemDetails(
                                subscription="sub_test"
                            )
                        ),
                    )
                ]
            ),
        )

        result = parse_invoice_paid(payload)

        assert result is not None
        assert result.subscription_id == "sub_test"
        assert result.customer_id == "cus_test"
        assert result.current_period_end == datetime.fromtimestamp(1234567890)
        assert result.status == "paid"

    def test_not_subscription_create_returns_none(self):
        """Test that non-subscription_create billing reason returns None."""
        payload = InvoicePayload(
            customer="cus_test",
            status="paid",
            billing_reason="manual",
            lines=InvoiceLines(data=[]),
        )

        result = parse_invoice_paid(payload)

        assert result is None

    def test_empty_lines_raises_error(self):
        """Test that empty lines raises ValueError."""
        payload = InvoicePayload(
            customer="cus_test",
            status="paid",
            billing_reason="subscription_create",
            lines=InvoiceLines(data=[]),
        )

        with pytest.raises(ValueError, match="No invoice lines found"):
            parse_invoice_paid(payload)

    def test_missing_parent_raises_error(self):
        """Test that missing parent raises ValueError."""
        payload = InvoicePayload(
            customer="cus_test",
            status="paid",
            billing_reason="subscription_create",
            lines=InvoiceLines(data=[InvoiceLine(period=InvoiceLinePeriod(end=1234567890))]),
        )

        with pytest.raises(ValueError, match="Missing parent"):
            parse_invoice_paid(payload)

    def test_missing_subscription_item_details_raises_error(self):
        """Test that missing subscription_item_details raises ValueError."""
        payload = InvoicePayload(
            customer="cus_test",
            status="paid",
            billing_reason="subscription_create",
            lines=InvoiceLines(
                data=[InvoiceLine(period=InvoiceLinePeriod(end=1234567890), parent=InvoiceLineParent())]
            ),
        )

        with pytest.raises(ValueError, match="Missing subscription_item_details"):
            parse_invoice_paid(payload)

    def test_missing_subscription_id_raises_error(self):
        """Test that missing subscription_id raises ValueError."""
        payload = InvoicePayload(
            customer="cus_test",
            status="paid",
            billing_reason="subscription_create",
            lines=InvoiceLines(
                data=[
                    InvoiceLine(
                        period=InvoiceLinePeriod(end=1234567890),
                        parent=InvoiceLineParent(subscription_item_details=InvoiceLineParentSubscriptionItemDetails()),
                    )
                ]
            ),
        )

        with pytest.raises(ValueError, match="Missing subscription_id"):
            parse_invoice_paid(payload)


class TestParseInvoicePaymentFailed:
    """Test parse_invoice_payment_failed function."""

    def test_valid_payload(self):
        """Test parsing invoice.payment_failed."""
        payload = InvoicePayload(
            customer="cus_test",
            status="failed",
            billing_reason="subscription_create",
            lines=InvoiceLines(
                data=[
                    InvoiceLine(
                        period=InvoiceLinePeriod(end=1234567890),
                        parent=InvoiceLineParent(
                            subscription_item_details=InvoiceLineParentSubscriptionItemDetails(
                                subscription="sub_test"
                            )
                        ),
                    )
                ]
            ),
        )

        result = parse_invoice_payment_failed(payload)

        assert result.subscription_id == "sub_test"
        assert result.customer_id == "cus_test"
        assert result.current_period_end == datetime.fromtimestamp(1234567890)
        assert result.status == "past_due"  # Always set to past_due

    def test_empty_lines_raises_error(self):
        """Test that empty lines raises ValueError."""
        payload = InvoicePayload(
            customer="cus_test",
            status="failed",
            lines=InvoiceLines(data=[]),
        )

        with pytest.raises(ValueError, match="No invoice lines found"):
            parse_invoice_payment_failed(payload)
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class InvoiceLinePeriod(BaseModel):
    end: Optional[int] = None


class InvoiceLineParentSubscriptionItemDetails(BaseModel):
    subscription: Optional[str] = None


class InvoiceLineParent(BaseModel):
    subscription_item_details: Optional[InvoiceLineParentSubscriptionItemDetails] = None


class InvoiceLine(BaseModel):
    period: Optional[InvoiceLinePeriod] = None
    parent: Optional[InvoiceLineParent] = None


class InvoiceLines(BaseModel):
    data: List[InvoiceLine] = []


# Validation schema - validates payload structure
# Make fields optional - validation logic is in the parser
class InvoicePayload(BaseModel):
    customer: Optional[str] = None
    status: Optional[str] = None
    billing_reason: Optional[str] = None
    lines: Optional[InvoiceLines] = None


# Parsed info returned to service
class InvoicePaidInfo(BaseModel):
    subscription_id: str
    customer_id: str
    current_period_end: datetime
    status: str


class InvoicePaymentFailedInfo(BaseModel):
    subscription_id: str
    customer_id: str
    current_period_end: datetime
    status: str = "past_due"


def _extract_subscription_from_line(line: InvoiceLine) -> str:
    """Extract subscription_id from invoice line."""
    if not line.parent:
        raise ValueError("Missing parent in invoice line")

    parent = line.parent
    if not parent.subscription_item_details:
        raise ValueError("Missing subscription_item_details in invoice line")

    sub_details = parent.subscription_item_details
    if not sub_details.subscription:
        raise ValueError("Missing subscription_id in subscription_item_details")

    return sub_details.subscription


def parse_invoice_paid(payload: InvoicePayload) -> InvoicePaidInfo | None:
    """Parse invoice.paid webhook payload.

    Returns None if invoice is not related to subscriptions.
    """
    # Ignore invoices not related to subscriptions
    if payload.billing_reason != "subscription_create":
        return None

    if not payload.lines or not payload.lines.data:
        raise ValueError("No invoice lines found in webhook payload")

    line = payload.lines.data[0]
    subscription_id = _extract_subscription_from_line(line)

    return InvoicePaidInfo(
        subscription_id=subscription_id,
        customer_id=payload.customer,
        current_period_end=datetime.fromtimestamp(line.period.end),
        status=payload.status,
    )


def parse_invoice_payment_failed(payload: InvoicePayload) -> InvoicePaymentFailedInfo:
    """Parse invoice.payment_failed webhook payload."""
    lines = payload.lines.data
    if not lines:
        raise ValueError("No invoice lines found in webhook payload")

    line = lines[0]
    subscription_id = _extract_subscription_from_line(line)

    return InvoicePaymentFailedInfo(
        subscription_id=subscription_id,
        customer_id=payload.customer,
        current_period_end=datetime.fromtimestamp(line.period.end),
        status="past_due",
    )
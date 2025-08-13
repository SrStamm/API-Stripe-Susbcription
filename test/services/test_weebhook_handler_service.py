from fastapi import HTTPException
from services.webhook_handler_service import WebhooksHandlerService
import pytest
from tasks.customer import (
    customer_created,
    customer_deleted,
)
from tasks.invoice import invoice_paid
from tasks.subscriptions import (
    customer_subscription_created,
    customer_subscription_deleted,
    customer_subscription_updated,
    customer_sub_basic,
)


def test_webhook_handler_service_error(mocker):
    web_serv = WebhooksHandlerService()

    with pytest.raises(HTTPException):
        web_serv.handle(event={})


def test_webhook_handler_invoice(mocker):
    mocker.patch("tasks.invoice.invoice_paid.delay")

    web_serv = WebhooksHandlerService()

    web_serv.handle(
        event={"type": "invoice.paid", "data": {"object": {"test": "webhook"}}}
    )

    invoice_paid.delay.assert_called_once_with({"test": "webhook"})


def test_webhook_handler_customer_success(mocker):
    mocker.patch("tasks.customer.customer_created.delay")
    mocker.patch("tasks.subscriptions.customer_sub_basic.delay")
    mocker.patch("tasks.customer.customer_deleted.delay")

    web_serv = WebhooksHandlerService()

    web_serv.handle(
        event={"type": "customer.created", "data": {"object": {"test": "webhook"}}}
    )

    web_serv.handle(
        event={"type": "customer.deleted", "data": {"object": {"test": "webhook"}}}
    )

    customer_created.delay.assert_called_once_with({"test": "webhook"})
    customer_sub_basic.delay.assert_called_once_with({"test": "webhook"})
    customer_deleted.delay.assert_called_once_with({"test": "webhook"})


def test_webhook_handler_subscriptions_success(mocker):
    mocker.patch("tasks.subscriptions.customer_subscription_created.delay")
    mocker.patch("tasks.subscriptions.customer_subscription_updated.delay")
    mocker.patch("tasks.subscriptions.customer_subscription_deleted.delay")

    web_serv = WebhooksHandlerService()

    web_serv.handle(
        event={
            "type": "customer.subscription.created",
            "data": {"object": {"test": "webhook"}},
        }
    )

    web_serv.handle(
        event={
            "type": "customer.subscription.updated",
            "data": {"object": {"test": "webhook"}},
        }
    )

    web_serv.handle(
        event={
            "type": "customer.subscription.deleted",
            "data": {"object": {"test": "webhook"}},
        }
    )

    customer_subscription_created.delay.assert_called_once_with({"test": "webhook"})
    customer_subscription_updated.delay.assert_called_once_with({"test": "webhook"})
    customer_subscription_deleted.delay.assert_called_once_with({"test": "webhook"})

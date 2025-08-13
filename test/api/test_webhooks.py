from fastapi import HTTPException
from test.conftest import client


def test_handle_webhooks_success(mocker, client):
    # Mock del evento
    mock_event = {"id": "evt_test", "type": "payment_intent.succeeded"}
    mocker.patch("api.webhooks.parse_webhook_event", return_value=mock_event)

    # Mockea el handler para no ejecutar lógica real
    mocker.patch("api.webhooks.WebhooksHandlerService")

    # Signature de stripe con formato válido
    stripe_signature = "t=123456789,v1=abc123"

    response = client.post(
        "/webhooks/", content=b"{}", headers={"stripe-signature": stripe_signature}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success"}


def test_handle_webhooks_not_header_error(client):
    response = client.post("/webhooks/", content=b"{}")

    assert response.status_code == 400
    assert response.json() == {"detail": "Stripe-Signature header missing"}


def test_handle_webhooks_db_error(mocker, client):
    # Mock del evento
    mock_event = {"id": "evt_test", "type": "payment_intent.succeeded"}
    mocker.patch("api.webhooks.parse_webhook_event", return_value=mock_event)

    # Mockea el handler para no ejecutar lógica real
    mocker.patch(
        "api.webhooks.WebhooksHandlerService",
        side_effect=HTTPException(status_code=400, detail="Simulated Error"),
    )

    # Signature de stripe con formato válido
    stripe_signature = "t=123456789,v1=abc123"

    response = client.post(
        "/webhooks/", content=b"{}", headers={"stripe-signature": stripe_signature}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Simulated Error"}


def test_handle_webhooks_unexpected_error(mocker, client):
    # Mock del evento
    mock_event = {"id": "evt_test", "type": "payment_intent.succeeded"}
    mocker.patch("api.webhooks.parse_webhook_event", return_value=mock_event)

    # Mockea el handler para no ejecutar lógica real
    mocker.patch(
        "api.webhooks.WebhooksHandlerService",
        side_effect=Exception("Simulated Error"),
    )

    # Signature de stripe con formato válido
    stripe_signature = "t=123456789,v1=abc123"

    response = client.post(
        "/webhooks/", content=b"{}", headers={"stripe-signature": stripe_signature}
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Webhook processing error: Simulated Error"}

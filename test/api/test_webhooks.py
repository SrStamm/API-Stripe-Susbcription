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


def test_handle_webhooks_not_header_error(mocker, client):
    response = client.post("/webhooks/", content=b"{}")

    assert response.status_code == 400
    assert response.json() == {"detail": "Stripe-Signature header missing"}

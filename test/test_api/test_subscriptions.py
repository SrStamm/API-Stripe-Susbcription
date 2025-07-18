from schemas import request
from schemas.request import SubID
from test.conftest import client, auth_headers
from services.subscription_service import SubscriptionService, get_subs_service
from models.subscription import Subscriptions
from datetime import datetime as dt
from main import app
import json


def test_get_all_success(client, mocker):
    serv_mocked = mocker.Mock(spec=SubscriptionService)

    sub_mocked = Subscriptions(
        id=1,
        user_id=1,
        plan_id=1,
        stripe_subscription_id="sub_mocked",
        status="incomplete",
        current_period_end=dt(2024, 12, 12, 0, 0),
    )

    serv_mocked.get_all_subscription.return_value = [sub_mocked]

    app.dependency_overrides[get_subs_service] = lambda: serv_mocked

    response = client.get("/subscriptions/all")

    assert response.status_code == 200

    list = response.json()

    for item in list:
        assert item["id"] == sub_mocked.id
        assert item["user_id"] == sub_mocked.user_id
        assert item["plan_id"] == sub_mocked.plan_id
        assert item["stripe_subscription_id"] == sub_mocked.stripe_subscription_id


def test_get_all_by_user_success(client, mocker, auth_headers):
    serv_mocked = mocker.Mock(spec=SubscriptionService)

    sub_mocked = Subscriptions(
        id=1,
        user_id=1,
        plan_id=1,
        stripe_subscription_id="sub_mocked",
        status="incomplete",
        current_period_end=dt(2024, 12, 12, 0, 0),
    )

    serv_mocked.get_all_subscription_by_user.return_value = sub_mocked

    app.dependency_overrides[get_subs_service] = lambda: serv_mocked

    response = client.get("/subscriptions/me", headers=auth_headers)

    assert response.status_code == 200

    item = response.json()

    assert item["id"] == sub_mocked.id
    assert item["user_id"] == sub_mocked.user_id
    assert item["plan_id"] == sub_mocked.plan_id
    assert item["stripe_subscription_id"] == sub_mocked.stripe_subscription_id


def test_get_by_id_success(client, mocker):
    serv_mocked = mocker.Mock(spec=SubscriptionService)

    sub_mocked = Subscriptions(
        id=1,
        user_id=1,
        plan_id=1,
        stripe_subscription_id="sub_mocked",
        status="incomplete",
        current_period_end=dt(2024, 12, 12, 0, 0),
    )

    serv_mocked.get_by_id.return_value = sub_mocked

    app.dependency_overrides[get_subs_service] = lambda: serv_mocked

    response = client.get("/subscriptions/sub_mocked")

    assert response.status_code == 200


def test_create_success(client, mocker, auth_headers):
    serv_mocked = mocker.Mock(spec=SubscriptionService)

    serv_mocked.create.return_value = {
        "detail": "Subscription created successfully",
        "subscription_id": "sub_id_mocked",
        "client_secret": "clientSecret_mocked",
        "status": "incomplete",
    }

    app.dependency_overrides[get_subs_service] = lambda: serv_mocked

    response = client.post(
        "/subscriptions/",
        headers=auth_headers,
        json={"plan_id": 1, "current_period_end": dt.now().isoformat()},
    )

    assert response.status_code == 200

    assert response.json() == {
        "detail": "Subscription created successfully",
        "subscription_id": "sub_id_mocked",
        "client_secret": "clientSecret_mocked",
        "status": "incomplete",
    }


def test_cancel_success(client, mocker, auth_headers):
    serv_mocked = mocker.Mock(spec=SubscriptionService)

    response_mocked = {"detail": "Subscription 1 has been cancelated with success"}

    serv_mocked.cancel.return_value = response_mocked

    app.dependency_overrides[get_subs_service] = lambda: serv_mocked

    data = {"id": "sub_mocked", "user_id": 1}

    response = client.request(
        "DELETE", "/subscriptions/", headers=auth_headers, json=data
    )

    assert response.status_code == 200

    assert response.json() == response_mocked

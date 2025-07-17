from services.plan_service import PlanService, get_plan_serv
from test.conftest import client, auth_headers
from main import app


def test_get_plans(client):
    response = client.get("/plans/")
    assert response.status_code == 200


def test_create_plan_success(mocker, client):
    create_product_mocked = mocker.patch(
        "services.plan_service.create_product",
        return_value={"id": "prod_mocked", "name": "test"},
    )

    create_price_mocked = mocker.patch(
        "services.plan_service.create_price",
        return_value={
            "id": "price_mocked",
            "unit_amount": 200,
            "recurring": {"interval": "month"},
        },
    )

    response = client.post(
        "/plans/",
        json={"name": "test", "description": "test", "amount": 200, "money": "usd"},
    )

    assert response.status_code == 200
    assert response.json() == {"detail": "New plan created: test"}

    create_product_mocked.assert_called_once()
    create_price_mocked.assert_called_once()


def test_update_price_for_plan_success(mocker, client):
    mock_plan_service = mocker.Mock(spec=PlanService)

    mock_plan_service.update.return_value = {"detail": "Price to Product updated"}

    app.dependency_overrides[get_plan_serv] = lambda: mock_plan_service

    update_data = {
        "id": "price_mocked",
        "name": "Update Plan Name",
        "description": "Update description",
        "amount": 300,
        "money": "usd",
        "interval": "month",
    }

    response = client.patch("/plans/", json=update_data)

    assert response.status_code == 200
    assert response.json() == {"detail": "Price to Product updated"}


def test_deactivate_plan_success(mocker, client):
    mock_plan_service = mocker.Mock(spec=PlanService)

    mock_plan_service.deactivate_plan.return_value = {
        "detail": "Plan and prices are been deactivated"
    }

    app.dependency_overrides[get_plan_serv] = lambda: mock_plan_service

    plan_id_to_deactivate = "price_mocked"

    deleted_data = {"id": plan_id_to_deactivate}

    response = client.request(
        "DELETE",
        "/plans/",
        json=deleted_data,
    )

    assert response.status_code == 200
    assert response.json() == {"detail": "Plan and prices are been deactivated"}

    mock_plan_service.deactivate_plan.assert_called_once_with(plan_id_to_deactivate)

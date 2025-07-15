from httpx._transports import mock
import pytest
from repositories.plan_repositories import PlanRepository
from schemas.exceptions import DatabaseError, PriceNotFound, ProductNotFound
from services.plan_service import PlanService


def test_create_success(mocker):
    repo_plan_mock = mocker.Mock(spec=PlanRepository)

    # Mockea las funciones de Stripe
    mock_create_product = mocker.patch(
        "services.plan_service.create_product",
        return_value={
            "id": "prod_mock_id",
            "name": "Test Product",
            "description": "A test product",
        },
    )
    mock_create_price = mocker.patch(
        "services.plan_service.create_price",
        return_value={
            "id": "price_mock_id",
            "unit_amount": 100,
            "currency": "uds",
            "recurring": {"interval": "month"},
            "product": "prod_mock_id",
        },
    )

    # Mockea el resultado
    repo_plan_mock.create.return_value = None

    # Instancia el Service
    plan_serv = PlanService(repo_plan_mock)

    response = plan_serv.create(
        name="test", description="test", amount=100, money="usd"
    )

    assert response == {"detail": "New plan created: Test Product"}

    mock_create_product.assert_called_once_with(name="test", description="test")
    mock_create_price.assert_called_once_with(
        amount=100, money="usd", product_id="prod_mock_id"
    )

    repo_plan_mock.create.assert_called_once_with(
        price_id="price_mock_id",
        name="test",
        description="test",
        price_cents=100,
        interval="month",
    )


def test_create_db_error(mocker):
    repo_plan_mock = mocker.Mock(spec=PlanRepository)

    # Mockea las funciones de Stripe
    mock_create_product = mocker.patch(
        "services.plan_service.create_product",
        return_value={
            "id": "prod_mock_id",
            "name": "Test Product",
            "description": "A test product",
        },
    )
    mock_create_price = mocker.patch(
        "services.plan_service.create_price",
        return_value={
            "id": "price_mock_id",
            "unit_amount": 100,
            "currency": "uds",
            "recurring": {"interval": "month"},
            "product": "prod_mock_id",
        },
    )

    # Mockea el resultado
    repo_plan_mock.create.side_effect = DatabaseError(
        error=Exception("Simulated DB error in create"), func="PlanRepository.create"
    )

    # Instancia el Service
    plan_serv = PlanService(repo_plan_mock)

    with pytest.raises(DatabaseError):
        plan_serv.create(name="test", description="test", amount=100, money="usd")

    mock_create_product.assert_called_once_with(name="test", description="test")
    mock_create_price.assert_called_once_with(
        amount=100, money="usd", product_id="prod_mock_id"
    )

    repo_plan_mock.create.assert_called_once_with(
        price_id="price_mock_id",
        name="test",
        description="test",
        price_cents=100,
        interval="month",
    )


def test_update_success(mocker):
    repo_plan_mock = mocker.Mock(spec=PlanRepository)

    # Mockea las funciones de Stripe

    mock_get_price = mocker.patch(
        "services.plan_service.get_price",
        return_value={
            "id": "old_price_id",
            "product": "prod_existing_id",
            "unit_amount": 50,
            "currency": "usd",
            "recurring": {"interval": "month"},
        },
    )
    mock_create_price = mocker.patch(
        "services.plan_service.create_price",
        return_value={
            "id": "price_mock_id",
            "unit_amount": 200,
            "currency": "uds",
            "recurring": {"interval": "month"},
            "product": "prod_mock_id",
        },
    )
    mock_deactivate_price = mocker.patch("services.plan_service.deactivate_price")
    mock_update_product = mocker.patch(
        "services.plan_service.update_product", return_value=None
    )

    repo_plan_mock.create.side_effect = DatabaseError(
        error=Exception("Simulated DB error in create"), func="PlanRepository.create"
    )

    # Mockea el resultado
    mock_product = mocker.Mock()
    mock_product.name = "test"
    repo_plan_mock.get_plan_by_id.return_value = mock_product
    repo_plan_mock.update.return_value = None

    # Instancia el Service
    plan_serv = PlanService(repo_plan_mock)

    response = plan_serv.update(id="old_price_id", amount=200, money="usd")

    assert response == {"detail": "Price to Product test updated"}

    mock_get_price.assert_called_once_with("old_price_id")
    mock_create_price.assert_called_once_with(
        amount=200, money="usd", product_id="prod_existing_id"
    )
    mock_deactivate_price.assert_called_once_with(id="old_price_id")
    mock_update_product.assert_not_called()

    repo_plan_mock.update.assert_called_once_with(
        old_price_id="old_price_id",
        new_price_id="price_mock_id",
        price_cents=200,
        interval="month",
    )


def test_update_not_found(mocker):
    repo_plan_mock = mocker.Mock(spec=PlanRepository)

    # Mockea el resultado
    repo_plan_mock.get_plan_by_id.return_value = None

    # Instancia el Service
    plan_serv = PlanService(repo_plan_mock)

    with pytest.raises(ProductNotFound):
        plan_serv.update(
            id="old_price_id",
            amount=200,
            money="usd",
        )

    repo_plan_mock.get_plan_by_id.assert_called_once_with("old_price_id")

    mock_product = mocker.Mock()
    mock_product.name = "test"
    repo_plan_mock.get_plan_by_id.return_value = mock_product

    mock_get_price = mocker.patch("services.plan_service.get_price", return_value=None)

    with pytest.raises(PriceNotFound):
        plan_serv.update(
            id="old_price_id",
            amount=200,
            money="usd",
        )


def test_update_db_error(mocker):
    repo_plan_mock = mocker.Mock(spec=PlanRepository)

    # Mockea las funciones de Stripe
    mock_get_price = mocker.patch(
        "services.plan_service.get_price",
        return_value={
            "id": "old_price_id",
            "product": "prod_existing_id",
            "unit_amount": 50,
            "currency": "usd",
            "recurring": {"interval": "month"},
        },
    )

    mock_create_price = mocker.patch(
        "services.plan_service.create_price",
        return_value={
            "id": "price_mock_id",
            "unit_amount": 200,
            "currency": "uds",
            "recurring": {"interval": "month"},
            "product": "prod_mock_id",
        },
    )

    mock_update_product = mocker.patch("services.plan_service.update_product")

    # Mockea el resultado
    mock_product = mocker.Mock()
    mock_product.name = "test"
    repo_plan_mock.get_plan_by_id.return_value = mock_product
    repo_plan_mock.update.side_effect = DatabaseError(
        error=Exception("Simulated DB error in create"), func="PlanRepository.update"
    )

    # Instancia el Service
    plan_serv = PlanService(repo_plan_mock)

    with pytest.raises(DatabaseError):
        plan_serv.update(
            id="old_price_id",
            amount=200,
            money="usd",
        )

    mock_get_price.assert_called_once_with("old_price_id")
    mock_create_price.assert_called_once_with(
        amount=200, money="usd", product_id="prod_existing_id"
    )
    mock_update_product.assert_not_called()

    repo_plan_mock.update.assert_called_once_with(
        old_price_id="old_price_id",
        new_price_id="price_mock_id",
        price_cents=200,
        interval="month",
    )


def test_deactivate_success(mocker):
    repo_plan_mock = mocker.Mock(spec=PlanRepository)

    # Mockea las funciones de Stripe
    mock_get_price = mocker.patch(
        "services.plan_service.get_price",
        return_value={
            "id": "old_price_id",
            "product": "prod_existing_id",
            "unit_amount": 50,
            "currency": "usd",
            "recurring": {"interval": "month"},
        },
    )

    mock_deactivate_product_and_prices = mocker.patch(
        "services.plan_service.deactivate_product_and_prices", return_value=None
    )

    # Instancia el Service
    plan_serv = PlanService(repo_plan_mock)

    response = plan_serv.deactivate_plan(
        id="old_price_id",
    )

    assert response == {"detail": "Plan and prices are been deactivated"}

    mock_get_price.assert_called_once_with("old_price_id")
    mock_deactivate_product_and_prices.assert_called_once_with("prod_existing_id")

    repo_plan_mock.delete.assert_called_once_with(
        "old_price_id",
    )

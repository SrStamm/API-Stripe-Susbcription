from models.plan import Plans
from models.user import Users
from schemas.exceptions import DatabaseError
from tasks.subscriptions import (
    customer_sub_basic,
    customer_subscription_created,
    customer_subscription_deleted,
    customer_subscription_updated,
)
from datetime import datetime
import pytest


def test_customer_sub_basic_success(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_sub_repo = mocker.Mock()
    mock_plan_repo = mocker.Mock()
    mock_user_repo = mocker.Mock()

    # Mockea las llamadas al repo
    mock_user_repo.get_user_by_customer_id.return_value = Users(
        id=1, email="test@gmail.com", stripe_customer_id=None
    )

    mock_plan_repo.get_plan_by_plan_id.return_value = Plans(
        id=1,
        stripe_price_id="price_mocked",
        name="test",
        description=None,
        price_cents=1000,
        interval="month",
    )

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch(
        "tasks.subscriptions.SubscriptionRepository", return_value=mock_sub_repo
    )
    mocker.patch("tasks.subscriptions.PlanRepository", return_value=mock_plan_repo)
    mocker.patch("tasks.subscriptions.UserRepository", return_value=mock_user_repo)

    # Mock del payload
    payload_mocked = {"id": "cus_mock_test"}

    # Llamada a la función
    customer_sub_basic(payload_mocked)

    # Verificaciones
    mock_sub_repo.update_for_user.assert_called_once_with(
        sub_id="sub_free",
        customer_id="cus_mock_test",
        status="active",
        current_period_end=None,
        is_active=True,
    )


def test_customer_sub_basic_user_error(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_sub_repo = mocker.Mock()
    mock_plan_repo = mocker.Mock()
    mock_user_repo = mocker.Mock()

    # Mockea las llamadas al repo
    mock_user_repo.get_user_by_customer_id.return_value = None

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch(
        "tasks.subscriptions.SubscriptionRepository", return_value=mock_sub_repo
    )
    mocker.patch("tasks.subscriptions.PlanRepository", return_value=mock_plan_repo)
    mocker.patch("tasks.subscriptions.UserRepository", return_value=mock_user_repo)

    # Mock del payload
    payload_mocked = {"id": "cus_mock_test"}

    # Llamada a la función
    with pytest.raises(Exception):
        customer_sub_basic(payload_mocked)


def test_customer_sub_basic_plan_error(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_sub_repo = mocker.Mock()
    mock_plan_repo = mocker.Mock()
    mock_user_repo = mocker.Mock()

    # Mockea las llamadas al repo
    mock_user_repo.get_user_by_customer_id.return_value = Users(
        id=1, email="test@gmail.com", stripe_customer_id=None
    )

    mock_plan_repo.get_plan_by_plan_id.return_value = None

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch(
        "tasks.subscriptions.SubscriptionRepository", return_value=mock_sub_repo
    )
    mocker.patch("tasks.subscriptions.PlanRepository", return_value=mock_plan_repo)
    mocker.patch("tasks.subscriptions.UserRepository", return_value=mock_user_repo)

    # Mock del payload
    payload_mocked = {"id": "cus_mock_test"}

    # Llamada a la función
    with pytest.raises(Exception):
        customer_sub_basic(payload_mocked)


def test_customer_sub_basic_db_error(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_sub_repo = mocker.Mock()
    mock_plan_repo = mocker.Mock()
    mock_user_repo = mocker.Mock()

    # Mockea las llamadas al repo
    mock_user_repo.get_user_by_customer_id.side_effect = DatabaseError(
        error="DB error false", func="get_user_by_customer_id"
    )

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch(
        "tasks.subscriptions.SubscriptionRepository", return_value=mock_sub_repo
    )
    mocker.patch("tasks.subscriptions.PlanRepository", return_value=mock_plan_repo)
    mocker.patch("tasks.subscriptions.UserRepository", return_value=mock_user_repo)

    # Mock del payload
    payload_mocked = {"id": "cus_mock_test"}

    # Llamada a la función
    with pytest.raises(DatabaseError):
        customer_sub_basic(payload_mocked)


def test_customer_subscription_created_success(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_sub_repo = mocker.Mock()

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch(
        "tasks.subscriptions.SubscriptionRepository", return_value=mock_sub_repo
    )

    # Mock del payload
    payload_mocked = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "test",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    current_period_end_mocked = datetime.fromtimestamp(
        payload_mocked["items"]["data"][0]["current_period_end"]
    )

    # Llamada a la función
    customer_subscription_created(payload_mocked)

    # Verificaciones
    mock_sub_repo.update_for_user.assert_called_once_with(
        sub_id=payload_mocked["id"],
        customer_id=payload_mocked["customer"],
        status=payload_mocked["status"],
        current_period_end=current_period_end_mocked,
        is_active=True,
    )


def test_customer_subscription_created_db_error(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_sub_repo = mocker.Mock()

    # Mockea la accion del repositorio
    mock_sub_repo.update_for_user.side_effect = DatabaseError(
        error="DB error false", func="update_for_user"
    )

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch(
        "tasks.subscriptions.SubscriptionRepository", return_value=mock_sub_repo
    )

    # Mock del payload
    payload_mocked = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "test",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    current_period_end_mocked = datetime.fromtimestamp(
        payload_mocked["items"]["data"][0]["current_period_end"]
    )

    # Llamada a la función
    with pytest.raises(DatabaseError):
        customer_subscription_created(payload_mocked)

    # Verificaciones
    mock_sub_repo.update_for_user.assert_called_once_with(
        sub_id=payload_mocked["id"],
        customer_id=payload_mocked["customer"],
        status=payload_mocked["status"],
        current_period_end=current_period_end_mocked,
        is_active=True,
    )


def test_customer_subscription_created_unexpected_error(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_sub_repo = mocker.Mock()

    # Mockea la accion del repositorio
    mock_sub_repo.update_for_user.side_effect = Exception("DB error false")

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch(
        "tasks.subscriptions.SubscriptionRepository", return_value=mock_sub_repo
    )

    # Mock del payload
    payload_mocked = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "test",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    current_period_end_mocked = datetime.fromtimestamp(
        payload_mocked["items"]["data"][0]["current_period_end"]
    )

    # Llamada a la función
    with pytest.raises(Exception):
        customer_subscription_created(payload_mocked)

    # Verificaciones
    mock_sub_repo.update_for_user.assert_called_once_with(
        sub_id=payload_mocked["id"],
        customer_id=payload_mocked["customer"],
        status=payload_mocked["status"],
        current_period_end=current_period_end_mocked,
        is_active=True,
    )


def test_customer_subscription_updated_success(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_sub_repo = mocker.Mock()

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch(
        "tasks.subscriptions.SubscriptionRepository", return_value=mock_sub_repo
    )

    # Mock del payload
    payload_mocked = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "incomplete",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    current_period_end_mocked = datetime.fromtimestamp(
        payload_mocked["items"]["data"][0]["current_period_end"]
    )

    # Llamada a la función
    customer_subscription_updated(payload_mocked)

    # Verificaciones
    mock_sub_repo.update_for_user.assert_called_once_with(
        sub_id=payload_mocked["id"],
        customer_id=payload_mocked["customer"],
        status=payload_mocked["status"],
        current_period_end=current_period_end_mocked,
        is_active=False,
    )


def test_customer_subscription_updated_unexpected_error(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_sub_repo = mocker.Mock()

    # Simulando error
    mock_sub_repo.update_for_user.side_effect = Exception("Unexpected Error Simulated")

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch(
        "tasks.subscriptions.SubscriptionRepository", return_value=mock_sub_repo
    )

    # Mock del payload
    payload_mocked = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "incomplete",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    current_period_end_mocked = datetime.fromtimestamp(
        payload_mocked["items"]["data"][0]["current_period_end"]
    )

    # Llamada a la función
    with pytest.raises(Exception):
        customer_subscription_updated(payload_mocked)

    # Verificaciones
    mock_sub_repo.update_for_user.assert_called_once_with(
        sub_id=payload_mocked["id"],
        customer_id=payload_mocked["customer"],
        status=payload_mocked["status"],
        current_period_end=current_period_end_mocked,
        is_active=False,
    )


def test_customer_subscription_updated_db_error(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_sub_repo = mocker.Mock()

    # Simulando error
    mock_sub_repo.update_for_user.side_effect = DatabaseError(
        error="Unexpected Error Simulated", func="update_for_user"
    )

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch(
        "tasks.subscriptions.SubscriptionRepository", return_value=mock_sub_repo
    )

    # Mock del payload
    payload_mocked = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "incomplete",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    current_period_end_mocked = datetime.fromtimestamp(
        payload_mocked["items"]["data"][0]["current_period_end"]
    )

    # Llamada a la función
    with pytest.raises(DatabaseError):
        customer_subscription_updated(payload_mocked)

    # Verificaciones
    mock_sub_repo.update_for_user.assert_called_once_with(
        sub_id=payload_mocked["id"],
        customer_id=payload_mocked["customer"],
        status=payload_mocked["status"],
        current_period_end=current_period_end_mocked,
        is_active=False,
    )


def test_customer_subscription_deleted_success(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_sub_repo = mocker.Mock()

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch(
        "tasks.subscriptions.SubscriptionRepository", return_value=mock_sub_repo
    )

    # Mock del payload
    payload_mocked = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "test",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    current_period_end_mocked = datetime.fromtimestamp(
        payload_mocked["items"]["data"][0]["current_period_end"]
    )

    # Llamada a la función
    customer_subscription_deleted(payload_mocked)

    # Verificaciones
    mock_sub_repo.cancel.assert_called_once_with(
        sub_id=payload_mocked["id"],
        customer_id=payload_mocked["customer"],
        status=payload_mocked["status"],
        current_period_end=current_period_end_mocked,
    )


def test_customer_subscription_deleted_db_error(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_sub_repo = mocker.Mock()

    # Mockea para que de error
    mock_sub_repo.cancel.side_effect = DatabaseError(
        error="DB error false", func="cancel"
    )

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch(
        "tasks.subscriptions.SubscriptionRepository", return_value=mock_sub_repo
    )

    # Mock del payload
    payload_mocked = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "test",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    current_period_end_mocked = datetime.fromtimestamp(
        payload_mocked["items"]["data"][0]["current_period_end"]
    )

    # Llamada a la función
    with pytest.raises(Exception):
        customer_subscription_deleted(payload_mocked)

    # Verificaciones
    mock_sub_repo.cancel.assert_called_once_with(
        sub_id=payload_mocked["id"],
        customer_id=payload_mocked["customer"],
        status=payload_mocked["status"],
        current_period_end=current_period_end_mocked,
    )


def test_customer_subscription_deleted_unexpected_error(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_sub_repo = mocker.Mock()

    # Mockea para que de error
    mock_sub_repo.cancel.side_effect = Exception("DB error false")

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch(
        "tasks.subscriptions.SubscriptionRepository", return_value=mock_sub_repo
    )

    # Mock del payload
    payload_mocked = {
        "id": "sub_mock_test",
        "customer": "cus_mock_test",
        "status": "test",
        "items": {"data": [{"current_period_end": 123456789}]},
    }

    current_period_end_mocked = datetime.fromtimestamp(
        payload_mocked["items"]["data"][0]["current_period_end"]
    )

    # Llamada a la función
    with pytest.raises(Exception):
        customer_subscription_deleted(payload_mocked)

    # Verificaciones
    mock_sub_repo.cancel.assert_called_once_with(
        sub_id=payload_mocked["id"],
        customer_id=payload_mocked["customer"],
        status=payload_mocked["status"],
        current_period_end=current_period_end_mocked,
    )

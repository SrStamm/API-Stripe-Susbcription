from repositories.subscription_repositories import SubscriptionRepository
from tasks.invoice import invoice_paid, invoice_payment_failed
import pytest
from datetime import datetime


@pytest.fixture
def mock_dependencies(mocker):
    # Mock de Session BD
    mock_session = mocker.Mock()
    mocker.patch("db.session.get_session", return_value=iter([mock_session]))

    # Mock Repository
    mock_repo = mocker.Mock(spec=SubscriptionRepository)
    mocker.patch(
        "repositories.subscription_repositories.SubscriptionRepository",
        return_value=mock_repo,
    )

    # Mock loger
    mock_logger = mocker.patch("core.logger.logger")

    return {"session": mock_session, "repo": mock_repo, "logger": mock_logger}


def test_invoice_paid_success(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_repo = mocker.Mock()

    # Configuración de los mocks
    mock_repo.get_subscription_for_user.return_value = {"id": "user_test"}

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch("tasks.invoice.SubscriptionRepository", return_value=mock_repo)

    # Payload de prueba
    payload_mocked = {
        "billing_reason": "subscription_create",
        "lines": {
            "data": [
                {
                    "parent": {
                        "subscription_item_details": {"subscription": "sub_test"},
                    },
                    "period": {"end": 123456789},
                }
            ],
        },
        "customer": "cus_test",
        "status": "paid",
    }

    # Ejecuta la tarea
    invoice_paid(payload_mocked)

    # Verificaciones
    mock_repo.get_subscription_for_user.assert_called_once_with(
        sub_id="sub_test", customer_id="cus_test"
    )

    mock_repo.update_for_user.assert_called_once_with(
        sub_id="sub_test",
        customer_id="cus_test",
        status="paid",
        current_period_end=datetime.fromtimestamp(123456789),
        is_active=True,
    )


def test_invoice_paid_not_relationated():
    payload_mocked = {}

    # Ejecuta la tarea
    invoice_paid(payload_mocked)


def test_invoice_paid_not_subscription():
    payload_mocked = {"billing_reason": "subscription_create"}

    with pytest.raises(Exception):
        invoice_paid(payload_mocked)


def test_not_subs_detail(mocker):
    payload_mocked = {
        "billing_reason": "subscription_create",
        "lines": {
            "data": [
                {
                    "parent": {"det": "asad"},
                }
            ],
        },
    }

    with pytest.raises(Exception):
        invoice_paid(payload_mocked)


def test_not_sub_id():
    payload_mocked = {
        "billing_reason": "subscription_create",
        "lines": {
            "data": [
                {
                    "parent": {"subscription_item_details": {}},
                }
            ],
        },
        "customer": None,
    }

    with pytest.raises(Exception):
        invoice_paid(payload_mocked)


def test_not_sub_error(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_repo = mocker.Mock()

    # Configuración de los mocks
    mock_repo.get_subscription_for_user.return_value = None

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch("tasks.invoice.SubscriptionRepository", return_value=mock_repo)

    # Payload de prueba
    payload_mocked = {
        "billing_reason": "subscription_create",
        "lines": {
            "data": [
                {
                    "parent": {
                        "subscription_item_details": {"subscription": "sub_test"},
                    },
                    "period": {"end": 123456789},
                }
            ],
        },
        "customer": "cus_test",
        "status": "paid",
    }

    # Ejecuta la tarea
    with pytest.raises(Exception):
        invoice_paid(payload_mocked)

    # Verificaciones
    mock_repo.get_subscription_for_user.assert_called_once_with(
        sub_id="sub_test", customer_id="cus_test"
    )


def test_invoice_payment_failed_success(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_repo = mocker.Mock()

    # Configuración de los mocks
    mock_repo.get_subscription_for_user.return_value = (
        {"id": "user_test", "stripe_subscription_id": "sub_test"},
    )

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch("tasks.invoice.SubscriptionRepository", return_value=mock_repo)

    # Payload de prueba
    payload_mocked = {
        "lines": {
            "data": [
                {
                    "parent": {
                        "subscription_item_details": {"subscription": "sub_test"},
                    },
                    "period": {"end": 123456789},
                }
            ],
        },
        "customer": "cus_test",
        "status": "failed",
    }

    # Ejecuta la tarea
    invoice_payment_failed(payload_mocked)

    # Verificaciones
    mock_repo.get_subscription_for_user.assert_called_once_with(
        sub_id="sub_test",
        customer_id="cus_test",
    )

    mock_repo.update_for_user.assert_called_once_with(
        sub_id="sub_test",
        customer_id="cus_test",
        status="failed",
        current_period_end=datetime.fromtimestamp(123456789),
        is_active=False,
    )


def test_invoice_payment_failed_bad_structure():
    # Payload de prueba
    payload_mocked = {}

    # Ejecuta la tarea
    with pytest.raises(Exception):
        invoice_payment_failed(payload_mocked)


def test_invoice_payment_failed_not_details():
    # Payload de prueba
    payload_mocked = {
        "lines": {
            "data": [
                {
                    "parent": {},
                }
            ],
        },
    }

    # Ejecuta la tarea
    with pytest.raises(Exception):
        invoice_payment_failed(payload_mocked)


def test_invoice_payment_failed_not_suscription(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_repo = mocker.Mock()

    # Configuración de los mocks
    mock_repo.get_subscription_for_user.return_value = None

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.invoice.get_session", return_value=iter([mock_session]))

    # Mockea el SubscriptionRepository
    mocker.patch("tasks.invoice.SubscriptionRepository", return_value=mock_repo)

    # Payload de prueba
    payload_mocked = {
        "lines": {
            "data": [
                {
                    "parent": {
                        "subscription_item_details": {"subscription": "sub_test"},
                    },
                    "period": {"end": 123456789},
                }
            ],
        },
        "customer": "cus_test",
        "status": "failed",
    }

    # Ejecuta la tarea
    with pytest.raises(Exception):
        invoice_payment_failed(payload_mocked)

    # Verificaciones
    mock_repo.get_subscription_for_user.assert_called_once_with(
        sub_id="sub_test",
        customer_id="cus_test",
    )

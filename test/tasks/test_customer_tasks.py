from models.user import Users
from schemas.exceptions import DatabaseError
from sqlalchemy.exc import SQLAlchemyError
from tasks.customer import customer_created, customer_deleted
import pytest


def test_customer_created_success(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_repo = mocker.Mock()

    # Mockea la interacción con la base de datos
    mock_repo.get_user_by_customer_id.return_value = None

    mock_repo.create.return_value = Users(
        id=1, email="test@gmail.com", stripe_customer_id="cus_mocked_id"
    )

    mock_repo.update.return_value = None

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.customer.get_session", return_value=iter([mock_session]))

    # Mockea el UserRepository
    mocker.patch("tasks.customer.UserRepository", return_value=mock_repo)

    # Payload para test
    test_payload = {"id": "cus_id", "email": "test@gmail.com"}

    customer_created(payload=test_payload)

    # Verificaciones
    mock_repo.get_user_by_customer_id.assert_called_once_with("cus_id")
    mock_repo.create.assert_called_once_with(email="test@gmail.com")
    mock_repo.update.assert_called_once_with(id=1, stripe_id="cus_id")


def test_customer_created_db_error(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_repo = mocker.Mock()

    # Mockea la interacción con la base de datos
    mock_repo.get_user_by_customer_id.side_effect = DatabaseError(
        error=SQLAlchemyError("db error"), func="get_user_by_customer_id"
    )

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.customer.get_session", return_value=iter([mock_session]))

    # Mockea el UserRepository
    mocker.patch("tasks.customer.UserRepository", return_value=mock_repo)

    # Payload para test
    test_payload = {"id": "cus_id", "email": "test@gmail.com"}

    with pytest.raises(DatabaseError):
        customer_created(payload=test_payload)


def test_customer_created_unexpected_error(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_repo = mocker.Mock()

    # Mockea la interacción con la base de datos
    mock_repo.get_user_by_customer_id.side_effect = Exception()

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.customer.get_session", return_value=iter([mock_session]))

    # Mockea el UserRepository
    mocker.patch("tasks.customer.UserRepository", return_value=mock_repo)

    # Payload para test
    test_payload = {"id": "cus_id", "email": "test@gmail.com"}

    with pytest.raises(Exception):
        customer_created(payload=test_payload)


def test_customer_deleted_success(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_repo = mocker.Mock()

    # Mockea la interacción con la base de datos
    mock_repo.delete.return_value = None

    mocker.patch(
        "repositories.user_repositories.UserRepository.get_user_by_customer_id",
        return_value=Users(id=1, email="test@gmail.com", stripe_customer_id="cus_id"),
    )

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.customer.get_session", return_value=iter([mock_session]))

    # Mockea el UserRepository
    mocker.patch("tasks.customer.UserRepository", return_value=mock_repo)

    # Payload para test
    test_payload = {"id": "cus_id"}

    customer_deleted(payload=test_payload)

    # Verificaciones
    mock_repo.delete.assert_called_once_with("cus_id")


def test_customer_deleted_db_error(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_repo = mocker.Mock()

    # Mockea la interacción con la base de datos
    mock_repo.delete.side_effect = DatabaseError(
        error=Exception(), func="UserRepository.delete"
    )

    mocker.patch(
        "repositories.user_repositories.UserRepository.get_user_by_customer_id",
        return_value=Users(id=1, email="test@gmail.com", stripe_customer_id="cus_id"),
    )

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.customer.get_session", return_value=iter([mock_session]))

    # Mockea el UserRepository
    mocker.patch("tasks.customer.UserRepository", return_value=mock_repo)

    # Payload para test
    test_payload = {"id": "cus_id"}

    with pytest.raises(DatabaseError):
        customer_deleted(payload=test_payload)

    # Verificaciones
    mock_repo.delete.assert_called_once_with("cus_id")


def test_customer_deleted_unexpected_error(mocker):
    # Mock de session y Repository
    mock_session = mocker.Mock()
    mock_repo = mocker.Mock()

    # Mockea la interacción con la base de datos
    mock_repo.delete.side_effect = Exception()

    mocker.patch(
        "repositories.user_repositories.UserRepository.get_user_by_customer_id",
        return_value=Users(id=1, email="test@gmail.com", stripe_customer_id="cus_id"),
    )

    # Mockea get_session para devolver la session mockeada
    mocker.patch("tasks.customer.get_session", return_value=iter([mock_session]))

    # Mockea el UserRepository
    mocker.patch("tasks.customer.UserRepository", return_value=mock_repo)

    # Payload para test
    test_payload = {"id": "cus_id"}

    with pytest.raises(Exception):
        customer_deleted(payload=test_payload)

    # Verificaciones
    mock_repo.delete.assert_called_once_with("cus_id")

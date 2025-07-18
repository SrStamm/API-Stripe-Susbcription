import pytest
from test.conftest import auth_headers, client
from models.user import CreateUser, Users
from repositories.user_repositories import UserRepository
from services.user_service import UserService
from schemas.exceptions import DatabaseError


def test_get_user_me(mocker):
    mock_repo = mocker.Mock()
    mock_serv = UserService(mock_repo)

    mock_repo.get_user_by_id.return_value = {
        "id": "1",
        "email": "test@gmail.com",
        "stripe_customer_id": "cus_a65sf46af",
    }

    response = mock_serv.get_user_me(1)
    assert response == {
        "id": "1",
        "email": "test@gmail.com",
        "stripe_customer_id": "cus_a65sf46af",
    }


def test_create_user_exists(client, mocker):
    mock_get_user_by_email = mocker.patch(
        "repositories.user_repositories.UserRepository.get_user_by_email",
        return_value=Users(id=1, email="falso@gmail.com", stripe_customer_id=None),
    )

    response = client.post("/users/", json={"email": "falso@gmail.com"})
    assert response.status_code == 200
    assert response.json() == {"detail": "User with these email exist"}

    mock_get_user_by_email.assert_called_once_with("falso@gmail.com")


def test_create_db_error(mocker):
    repo_mock = mocker.Mock(spec=UserRepository)

    repo_mock.get_user_by_email.return_value = None

    repo_mock.create.side_effect = DatabaseError(
        error=Exception("Simulated DB error on create"), func="UserRepository.create"
    )

    mocker.patch(
        "core.stripe_test.createCustomer",
        return_value={"id": "cus_mock_id_123", "email": "test@gmail.com"},
    )

    serv = UserService(repo_mock)

    with pytest.raises(DatabaseError) as excinfo:
        serv.create(CreateUser(email="test@gmail.com"))

    # Aserciones adicionales:
    repo_mock.get_user_by_email.assert_called_once_with("test@gmail.com")
    repo_mock.create.assert_called_once_with("test@gmail.com")

    # Asegúrate de que repo.update no fue llamado si el error ocurre en repo.create
    repo_mock.update.assert_not_called()

    assert (
        "500: database error en UserRepository.create: Simulated DB error on create"
        in str(excinfo.value)
    )


def test_delete_success(mocker):
    repo_mock = mocker.Mock(spec=UserRepository)

    mock_delete_customer = mocker.patch(
        "services.user_service.deleteCustomer",
        side_effect=Exception("Simulated Unknown error"),
    )

    serv = UserService(repo_mock)

    with pytest.raises(Exception):
        serv.delete(customer_id="cus_mock_id_123")

    mock_delete_customer.assert_called_once_with("cus_mock_id_123")

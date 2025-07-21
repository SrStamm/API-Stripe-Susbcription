from dependencies.auth import get_current_user
from test.conftest import client, auth_headers
from models.user import Users
from main import app


def test_get_users(mocker, client):
    user_mocked = Users(id=1, email="test@gmail.com", stripe_customer_id=None)

    mocker.patch(
        "repositories.user_repositories.UserRepository.get_users",
        return_value=[user_mocked],
    )

    response = client.get("/users/")

    assert response.status_code == 200

    list = response.json()

    for r in list:
        assert r == {"id": 1, "email": "test@gmail.com", "stripe_customer_id": None}


def test_get_me(client, auth_headers):
    response = client.get("/users/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "test@gmail.com",
        "stripe_customer_id": None,
    }


def test_create_user_success(client, mocker):
    # Mock para simular que el usuario no existe
    mock_get_user_by_email = mocker.patch(
        "repositories.user_repositories.UserRepository.get_user_by_email",
        return_value=None,
    )

    # Mock para simular la creacion de un usuario en la DB
    mock_user_create_repo = mocker.patch(
        "repositories.user_repositories.UserRepository.create",
        return_value=Users(id=1, email="falso@gmail.com", stripe_customer_id=None),
    )

    # Mock para update
    mock_user_repo_update = mocker.patch(
        "repositories.user_repositories.UserRepository.update"
    )

    # Mock para stripe
    mock_create_customer = mocker.patch(
        "services.user_service.createCustomer",
        return_value={
            "id": "cus_mock_id_123",
            "email": "falso@gmail.com",
        },
    )

    response = client.post("/users/", json={"email": "falso@gmail.com"})
    assert response.status_code == 200
    assert response.json() == {"detail": "User created"}

    mock_get_user_by_email.assert_called_once_with("falso@gmail.com")

    mock_user_create_repo.assert_called_once_with("falso@gmail.com")

    mock_create_customer.assert_called_once_with("falso@gmail.com", 1)

    mock_user_repo_update.assert_called_once_with(id=1, stripe_id="cus_mock_id_123")


# def test_create_user_exists(client, mocker):
#     # Mock para simular que el usuario no existe
#     mock_get_user_by_email = mocker.patch(
#         "repositories.user_repositories.UserRepository.get_user_by_email",
#         return_value=Users(id=1, email="falso@gmail.com", stripe_customer_id=None),
#     )
#
#     response = client.post("/users/", json={"email": "falso@gmail.com"})
#     assert response.status_code == 200
#     assert response.json() == {"detail": "User with these email exist"}
#
#     mock_get_user_by_email.assert_called_once_with("falso@gmail.com")


def test_delete(mocker, client, auth_headers):
    customer_id_to_delete = "cus_mock_id_from_user"

    def overrides_get_current_user():
        return Users(
            id=1, email="test@gmail.com", stripe_customer_id=customer_id_to_delete
        )

    app.dependency_overrides[get_current_user] = overrides_get_current_user

    # Mock para stripe.deleteCustomer
    mock_delete_customer = mocker.patch(
        "services.user_service.deleteCustomer",
        return_value={
            "id": "cus_mock_id_to_delete",
            "deleted": True,
        },
    )

    response = client.delete("/users/", headers=auth_headers)

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"customer_id": "cus_mock_id_to_delete", "deleted": True}

    mock_delete_customer.assert_called_once_with(customer_id_to_delete)


def test_delete_error(mocker, client, auth_headers):
    def overrides_get_current_user():
        return Users(id=1, email="test@gmail.com", stripe_customer_id=None)

    app.dependency_overrides[get_current_user] = overrides_get_current_user

    # Mock para stripe.deleteCustomer
    mock_delete_customer = mocker.patch(
        "services.user_service.deleteCustomer",
    )

    response = client.delete("/users/", headers=auth_headers)

    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json() == {"detail": "User 1 not have CustomerId to Stripe"}

    mock_delete_customer.assert_not_called()

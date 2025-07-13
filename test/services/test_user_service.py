from services.user_service import UserService


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


def test_create(mocker):
    mock_repo = mocker.Mock()
    mock_serv = UserService(mock_repo)

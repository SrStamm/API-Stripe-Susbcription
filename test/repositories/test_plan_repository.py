import pytest
from sqlalchemy.exc import SQLAlchemyError
from models.plan import Plans
from repositories.plan_repositories import PlanRepository
from schemas.exceptions import DatabaseError, PlanNotFound


def test_get_plan_by_plan_id_success(mocker):
    mock_session = mocker.Mock()
    plan_mocked = Plans(
        id=1,
        stripe_price_id="pr_86464",
        name="test",
        description=None,
        price_cents=200,
        interval="month",
    )
    mock_session.exec.return_value.first.return_value = plan_mocked

    repo = PlanRepository(mock_session)
    repo.get_plan_by_plan_id(1)


def test_create(mocker):
    mock_session = mocker.Mock()

    repo = PlanRepository(mock_session)

    repo.create(
        price_id="pr_86464",
        name="test",
        description=None,
        price_cents=100,
        interval="month",
    )


def test_create_db_error(mocker):
    mock_session = mocker.Mock()

    mock_session.commit.side_effect = SQLAlchemyError("ERROR INTERNO")

    repo = PlanRepository(mock_session)

    with pytest.raises(DatabaseError):
        repo.create(
            price_id="pr_86464",
            name="test",
            description=None,
            price_cents=100,
            interval="month",
        )


def test_update(mocker):
    mock_session = mocker.Mock()

    plan_mocked = mocker.Mock()
    plan_mocked.price_id = "pr_5165468"
    plan_mocked.price_cents = 50

    mock_session.exec.return_value = plan_mocked
    repo = PlanRepository(mock_session)

    repo.update(
        old_price_id="pr_5165468",
        new_price_id="pr_86464",
        price_cents=100,
        interval="month",
        name="test_2",
        description="Test",
    )


def test_update_not_found_error(mocker):
    mock_session = mocker.Mock()

    mock_session.exec.return_value.first.return_value = None

    repo = PlanRepository(mock_session)

    with pytest.raises(PlanNotFound):
        repo.update(
            old_price_id="pr_5165468",
            new_price_id="pr_86464",
        )


def test_update_db_error(mocker):
    mock_session = mocker.Mock()

    mock_session.exec.side_effect = SQLAlchemyError("ERROR INTERNO")

    repo = PlanRepository(mock_session)

    with pytest.raises(DatabaseError):
        repo.update(
            old_price_id="pr_5165468",
            new_price_id="pr_86464",
        )


def test_delete_success(mocker):
    mock_session = mocker.Mock()

    # Mock de varios planes
    plan_mocked_1 = mocker.Mock()
    plan_mocked_1.id = 1
    plan_mocked_1.price_id = "pr_5165468"

    plan_mocked_2 = mocker.Mock()
    plan_mocked_2.id = 2
    plan_mocked_2.price_id = "pr_516546854648"

    mock_session.exec.return_value.all.return_value = [plan_mocked_1, plan_mocked_2]
    repo = PlanRepository(mock_session)

    repo.delete(price_id="pr_5165468")


def test_delete_not_found(mocker):
    mock_session = mocker.Mock()

    mock_session.exec.return_value.all.return_value = []
    repo = PlanRepository(mock_session)

    with pytest.raises(PlanNotFound):
        repo.delete(price_id="pr_5165468")


def test_delete_db_error(mocker):
    mock_session = mocker.Mock()

    mock_session.exec.side_effect = SQLAlchemyError("ERROR INTERNO")
    repo = PlanRepository(mock_session)

    with pytest.raises(DatabaseError):
        repo.delete(price_id="pr_5165468")

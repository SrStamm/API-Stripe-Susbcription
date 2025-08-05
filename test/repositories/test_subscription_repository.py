from datetime import datetime as dt

import pytest
from sqlalchemy.exc import SQLAlchemyError
from models.subscription import Subscriptions
from repositories.subscription_repositories import SubscriptionRepository
from schemas.enums import SubscriptionTier
from schemas.exceptions import DatabaseError, SubscriptionNotFound


def test_get_all_subscriptions(mocker):
    mock_session = mocker.Mock()

    mock_subscription = Subscriptions(
        id=1,
        user_id=1,
        plan_id=1,
        stripe_subscription_id="sub_mocked",
        status="incomplete",
        current_period_end=dt.now(),
    )

    mock_session.exec.return_value.all.return_value = [mock_subscription]

    repo = SubscriptionRepository(mock_session)

    response = repo.get_all_subscription()

    for r in response:
        assert r == mock_subscription


def test_get_all_subscriptions_by_user(mocker):
    mock_session = mocker.Mock()

    mock_subscription = Subscriptions(
        id=1,
        user_id=1,
        plan_id=1,
        stripe_subscription_id="sub_mocked",
        status="incomplete",
        current_period_end=dt.now(),
    )

    mock_session.exec.return_value.all.return_value = [mock_subscription]

    repo = SubscriptionRepository(mock_session)

    response = repo.get_all_subscription_by_user(1)

    for r in response:
        assert r == mock_subscription


def test_create_success(mocker):
    mock_session = mocker.Mock()

    repo = SubscriptionRepository(mock_session)

    repo.create(
        user_id=1,
        plan_id=1,
        subscription_id="sub_46846848",
        status="incomplete",
        current_period_end=dt.now(),
        tier=SubscriptionTier.free,
    )


def test_create_db_error(mocker):
    mock_session = mocker.Mock()

    mock_session.commit.side_effect = SQLAlchemyError("DB ERROR")

    repo = SubscriptionRepository(mock_session)

    with pytest.raises(DatabaseError):
        repo.create(
            user_id=1,
            plan_id=1,
            subscription_id="sub_46846848",
            status="incomplete",
            current_period_end=dt.now(),
            tier=SubscriptionTier.free,
        )


def test_update_success(mocker):
    mock_session = mocker.Mock()
    sub_mocked = mocker.Mock(spec=Subscriptions)

    mock_session.exec.return_value.first.return_value = sub_mocked

    repo = SubscriptionRepository(mock_session)

    repo.update(
        id="sub_46846848",
        status="incomplete",
        current_period_end=dt.now(),
    )


def test_update_not_found_error(mocker):
    mock_session = mocker.Mock()

    mock_session.exec.return_value.first.return_value = None

    repo = SubscriptionRepository(mock_session)

    with pytest.raises(SubscriptionNotFound):
        repo.update(
            id="sub_46846848",
            status="incomplete",
            current_period_end=dt.now(),
        )


def test_update_db_error(mocker):
    mock_session = mocker.Mock()

    mock_session.exec.side_effect = SQLAlchemyError("ERROR INTERNO")

    repo = SubscriptionRepository(mock_session)

    with pytest.raises(DatabaseError):
        repo.update(
            id="sub_46846848",
            status="incomplete",
            current_period_end=dt.now(),
        )


def test_update_for_user_success(mocker):
    mock_session = mocker.Mock()
    sub_mocked = mocker.Mock(spec=Subscriptions)

    mock_session.exec.return_value.first.return_value = sub_mocked

    repo = SubscriptionRepository(mock_session)

    repo.update_for_user(
        sub_id="sub_46846848",
        customer_id="cus_5468468",
        status="incomplete",
        is_active=True,
        current_period_end=dt.now(),
    )


def test_update_for_user_not_found_error(mocker):
    mock_session = mocker.Mock()

    mock_session.exec.return_value.first.return_value = None

    repo = SubscriptionRepository(mock_session)

    with pytest.raises(SubscriptionNotFound):
        repo.update_for_user(
            sub_id="sub_46846848",
            customer_id="cus_5468468",
            is_active=False,
            status="incomplete",
            current_period_end=dt.now(),
        )


def test_update_for_user_db_error(mocker):
    mock_session = mocker.Mock()

    mock_session.exec.side_effect = SQLAlchemyError("ERROR INTERNO")

    repo = SubscriptionRepository(mock_session)

    with pytest.raises(DatabaseError):
        repo.update_for_user(
            sub_id="sub_46846848",
            customer_id="cus_5468468",
            is_active=False,
            status="incomplete",
            current_period_end=dt.now(),
        )


def test_cancel_success(mocker):
    mock_session = mocker.Mock()
    sub_mocked = mocker.Mock(spec=Subscriptions)

    mock_session.exec.return_value.first.return_value = sub_mocked

    repo = SubscriptionRepository(mock_session)

    repo.cancel(
        sub_id="sub_46846848",
        customer_id="cus_5468468",
        status="incomplete",
        current_period_end=dt.now(),
    )


def test_cancel_not_found_error(mocker):
    mock_session = mocker.Mock()

    mock_session.exec.return_value.first.return_value = None

    repo = SubscriptionRepository(mock_session)

    with pytest.raises(SubscriptionNotFound):
        repo.cancel(
            sub_id="sub_46846848",
            customer_id="cus_5468468",
            status="incomplete",
            current_period_end=dt.now(),
        )


def test_cancel_db_error(mocker):
    mock_session = mocker.Mock()

    mock_session.exec.side_effect = SQLAlchemyError("ERROR INTERNO")

    repo = SubscriptionRepository(mock_session)

    with pytest.raises(DatabaseError):
        repo.cancel(
            sub_id="sub_46846848",
            customer_id="cus_5468468",
            status="incomplete",
            current_period_end=dt.now(),
        )

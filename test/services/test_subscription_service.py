import pytest
from models.plan import Plans
from models.subscription import Subscriptions
from models.user import Users
from schemas.enums import SubscriptionTier
from schemas.exceptions import (
    DatabaseError,
    PlanNotFound,
    UserNotFoundError,
    UserNotSubscriptedError,
    UserSubscriptedError,
)
from schemas.request import SubID, SubscriptionCreate
from services.subscription_service import SubscriptionService
from datetime import datetime as dt


def test_get_by_id_success(mocker):
    # Mockea los repos para Service
    sub_repo_mock = mocker.Mock()
    user_repo_mock = mocker.Mock()
    plan_repo_mock = mocker.Mock()

    # Mockea la respuesta
    sub_repo_mock.get_subscription_by_id.return_value = Subscriptions(
        id=1,
        user_id=1,
        plan_id=1,
        stripe_subscription_id="sub_mock_123",
        status="incomplete",
        current_period_end=dt.now(),
    )

    # Instancia el Service
    serv = SubscriptionService(
        repo=sub_repo_mock, user_repo=user_repo_mock, plan_repo=plan_repo_mock
    )

    serv.get_by_id("sub_mock_123")

    # Verifica que la funcion se haya llamado
    sub_repo_mock.get_subscription_by_id.assert_called_once_with("sub_mock_123")


def test_get_all_subscriptions_success(mocker):
    sub_repo_mock = mocker.Mock()
    user_repo_mock = mocker.Mock()
    plan_repo_mock = mocker.Mock()

    sub_repo_mock.get_all_subscription.return_value = [
        Subscriptions(
            id=1,
            user_id=1,
            plan_id=1,
            stripe_subscription_id="sub_mock_123",
            status="incomplete",
            current_period_end=dt.now(),
        ),
        Subscriptions(
            id=2,
            user_id=1,
            plan_id=2,
            stripe_subscription_id="sub_mock_321",
            status="paid",
            current_period_end=dt.now(),
        ),
    ]

    serv = SubscriptionService(
        repo=sub_repo_mock, user_repo=user_repo_mock, plan_repo=plan_repo_mock
    )

    serv.get_all_subscription()

    sub_repo_mock.get_all_subscription.assert_called_once_with()


def test_get_all_subscriptions_by_user_success(mocker):
    sub_repo_mock = mocker.Mock()
    user_repo_mock = mocker.Mock()
    plan_repo_mock = mocker.Mock()

    sub_repo_mock.get_all_subscription_by_user.return_value = [
        Subscriptions(
            id=1,
            user_id=1,
            plan_id=1,
            stripe_subscription_id="sub_mock_123",
            status="incomplete",
            current_period_end=dt.now(),
        ),
        Subscriptions(
            id=2,
            user_id=1,
            plan_id=2,
            stripe_subscription_id="sub_mock_321",
            status="paid",
            current_period_end=dt.now(),
        ),
    ]

    serv = SubscriptionService(
        repo=sub_repo_mock, user_repo=user_repo_mock, plan_repo=plan_repo_mock
    )

    serv.get_all_subscription_by_user(id=1)

    sub_repo_mock.get_all_subscription_by_user.assert_called_once_with(1)


def test_create_success(mocker):
    sub_repo_mock = mocker.Mock()
    user_repo_mock = mocker.Mock()
    plan_repo_mock = mocker.Mock()

    # Mockea los repos utilizados
    mock_user = Users(id=1, email="test@gmail.com", stripe_customer_id="cus_mock_123")
    user_repo_mock.get_user_by_id.return_value = mock_user

    mock_plan = Plans(
        id=1,
        stripe_price_id="pr_mock_123",
        name="Test",
        description=None,
        price_cents=200,
        interval="month",
    )
    plan_repo_mock.get_plan_by_tier.return_value = mock_plan

    sub_repo_mock.get_all_subscription_by_user.return_value = []

    mock_current_period_end = dt(2025, 7, 15, 10, 0, 0)

    # Mockea las funciones de Stripe
    mock_create_subscription = mocker.patch(
        "services.subscription_service.createSubscription",
        return_value={
            "current_period_end": mock_current_period_end,
            "subscription_id": "sub_mock_123",
            "clientSecret": "mock_client_secret",
            "status": "incomplete",
        },
    )

    serv = SubscriptionService(
        repo=sub_repo_mock, user_repo=user_repo_mock, plan_repo=plan_repo_mock
    )

    subscription_data = SubscriptionCreate(
        tier=SubscriptionTier.free, current_period_end=mock_current_period_end
    )

    serv.create(
        data=subscription_data,
        user_id=1,
    )

    # Verifica que hayan sido llamada las funciones
    sub_repo_mock.create.assert_called_once_with(
        plan_id=1,
        subscription_id="sub_mock_123",
        current_period_end=mock_current_period_end,
        user_id=1,
        status="incomplete",
        tier=SubscriptionTier.free,
    )

    mock_create_subscription.assert_called_once_with(
        customer_id=mock_user.stripe_customer_id,
        price_id=mock_plan.stripe_price_id,
        plan_id=mock_plan.id,
        user_id=1,
    )


def test_create_not_found(mocker):
    sub_repo_mock = mocker.Mock()
    user_repo_mock = mocker.Mock()
    plan_repo_mock = mocker.Mock()

    # Mockea los repos utilizados
    user_repo_mock.get_user_by_id.return_value = None

    serv = SubscriptionService(
        repo=sub_repo_mock, user_repo=user_repo_mock, plan_repo=plan_repo_mock
    )

    subscription_data = SubscriptionCreate(
        tier=SubscriptionTier.free, current_period_end=dt.now()
    )

    with pytest.raises(UserNotFoundError):
        serv.create(
            data=subscription_data,
            user_id=1,
        )

    mock_user = Users(id=1, email="test@gmail.com", stripe_customer_id="cus_mock_123")
    user_repo_mock.get_user_by_id.return_value = mock_user

    plan_repo_mock.get_plan_by_tier.return_value = None

    with pytest.raises(PlanNotFound):
        serv.create(
            data=subscription_data,
            user_id=1,
        )

    mock_plan = Plans(
        id=1,
        stripe_price_id="pr_mock_123",
        name="Test",
        description=None,
        price_cents=200,
        interval="month",
    )
    plan_repo_mock.get_plan_by_tier.return_value = mock_plan

    sub_repo_mock.get_all_subscription_by_user.return_value = [
        Subscriptions(
            id=1,
            user_id=mock_user.id,
            plan_id=mock_plan.id,
            stripe_subscription_id="sub_mock_123",
            status="incomplete",
            current_period_end=dt.now(),
        )
    ]

    with pytest.raises(UserSubscriptedError):
        serv.create(
            data=subscription_data,
            user_id=1,
        )


def test_create_db_error(mocker):
    # Mock repositories
    sub_repo_mock = mocker.Mock()
    user_repo_mock = mocker.Mock()
    plan_repo_mock = mocker.Mock()

    # Mock data
    subscription_data = SubscriptionCreate(
        tier=SubscriptionTier.free, current_period_end=dt.now()
    )

    mock_user = Users(id=1, email="test@gmail.com", stripe_customer_id="cus_mock_123")

    mock_plan = Plans(
        id=1,
        stripe_price_id="pr_mock_123",
        name="Test",
        description=None,
        price_cents=200,
        interval="month",
    )

    # Mock repo funciones
    user_repo_mock.get_user_by_id.return_value = mock_user

    plan_repo_mock.get_plan_by_tier.return_value = mock_plan

    sub_repo_mock.get_all_subscription_by_user.return_value = []

    # Mock stripe funciones
    mock_sub_id = "mock_sub_id"
    mock_create_subscription = mocker.patch(
        "services.subscription_service.createSubscription",
        return_value={
            "current_period_end": None,
            "subscription_id": mock_sub_id,
            "status": "incomplete",
        },
    )

    sub_repo_mock.create.side_effect = DatabaseError(
        error=Exception("simulated DB Error"), func="SubscriptionRepository.create"
    )

    serv = SubscriptionService(sub_repo_mock, user_repo_mock, plan_repo_mock)

    with pytest.raises(DatabaseError):
        serv.create(
            data=subscription_data,
            user_id=1,
        )

    mock_create_subscription.assert_called_once_with(
        customer_id=mock_user.stripe_customer_id,
        price_id=mock_plan.stripe_price_id,
        user_id=mock_user.id,
        plan_id=mock_plan.id,
    )


def test_cancel_success(mocker):
    sub_repo_mock = mocker.Mock()
    user_repo_mock = mocker.Mock()
    plan_repo_mock = mocker.Mock()

    mock_current_period_end = dt(2025, 7, 15, 10, 0, 0)

    # Mockea los repos utilizados
    mock_user = Users(id=1, email="test@gmail.com", stripe_customer_id="cus_mock_123")
    user_repo_mock.get_user_by_id.return_value = mock_user

    mock_sub = Subscriptions(
        id=1,
        user_id=1,
        plan_id=1,
        stripe_subscription_id="sub_mock_123",
        status="incomplete",
        current_period_end=mock_current_period_end,
    )
    sub_repo_mock.get_subscription_for_user.return_value = mock_sub

    # Mockea las funciones de Stripe
    mock_cancel_subscription = mocker.patch(
        "services.subscription_service.cancelSubscription", return_value=None
    )

    serv = SubscriptionService(
        repo=sub_repo_mock, user_repo=user_repo_mock, plan_repo=plan_repo_mock
    )

    serv.cancel(
        data=SubID(id=mock_sub.stripe_subscription_id),
        user_id=1,
    )

    # Verifica que hayan sido llamada las funciones
    mock_cancel_subscription.assert_called_once_with(mock_sub.stripe_subscription_id)


def test_cancel_not_found(mocker):
    sub_repo_mock = mocker.Mock()
    user_repo_mock = mocker.Mock()
    plan_repo_mock = mocker.Mock()

    # Mockea los repos utilizados
    mock_user = Users(id=1, email="test@gmail.com", stripe_customer_id="cus_mock_123")
    user_repo_mock.get_user_by_id.return_value = mock_user

    sub_repo_mock.get_subscription_for_user.return_value = None

    serv = SubscriptionService(
        repo=sub_repo_mock, user_repo=user_repo_mock, plan_repo=plan_repo_mock
    )

    with pytest.raises(UserNotSubscriptedError):
        serv.cancel(
            data=SubID(id="sub_mock_123"),
            user_id=1,
        )

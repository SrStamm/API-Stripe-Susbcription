from test.conftest import client
from services.subscription_service import SubscriptionService, get_subs_service
from models.subscription import Subscriptions
from datetime import datetime as dt
from main import app


def test_get_by_id_success(client, mocker):
    serv_mocked = mocker.Mock(spec=SubscriptionService)

    sub_mocked = Subscriptions(
        id=1,
        user_id=1,
        plan_id=1,
        stripe_subscription_id="sub_mocked",
        status="incomplete",
        current_period_end=dt.now(),
    )

    serv_mocked.get_by_id.return_value = sub_mocked

    app.dependency_overrides[get_subs_service] = serv_mocked

    response = client.get("/subscriptions/sub_mocked")

    assert response.status_code == 200
    assert response.json() == sub_mocked

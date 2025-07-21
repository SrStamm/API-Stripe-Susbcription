from repositories.subscription_repositories import SubscriptionRepository
import pytest


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

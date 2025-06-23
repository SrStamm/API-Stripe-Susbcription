from fastapi import Depends
from repositories.subscription_repositories import SubscriptionRepository, get_subs_repo


class SubscriptionService:
    def __init__(self, repo: SubscriptionRepository) -> None:
        self.repo = repo

    def get_by_id(self, id: str):
        return self.repo.get_subscription_by_id(id)

    def get_all_subscription(self):
        return self.repo.get_all_subscription()


def get_subs_service(
    repo: SubscriptionRepository = Depends(get_subs_repo),
) -> SubscriptionService:
    return SubscriptionService(repo)

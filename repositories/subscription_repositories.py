from fastapi import Depends
from db.session import Session, get_session, select
from models.subscription import Subscriptions


class SubscriptionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_subscription_by_id(self, id: str):
        stmt = select(Subscriptions).where(Subscriptions.id == id)
        return self.session.exec(stmt).first()

    def get_all_subscription(self):
        stmt = select(Subscriptions)
        return self.session.exec(stmt).all()


def get_subs_repo(session: Session = Depends(get_session)):
    return SubscriptionRepository(session)

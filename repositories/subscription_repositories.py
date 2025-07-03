from datetime import datetime
from typing import Optional
from fastapi import Depends
from db.session import Session, get_session, select
from models.subscription import Subscriptions
from models.user import Users


class SubscriptionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_subscription_by_id(self, id: str):
        stmt = select(Subscriptions).where(Subscriptions.stripe_subscription_id == id)
        return self.session.exec(stmt).first()

    def get_all_subscription(self):
        stmt = select(Subscriptions)
        return self.session.exec(stmt).all()

    def get_all_subscription_by_user(self, id: int):
        stmt = select(Users).where(Users.id == id)
        user = self.session.exec(stmt).first()
        return user.subscriptions

    def get_subscription_for_user(self, sub_id: str, customer_id: str):
        stmt = (
            select(Subscriptions)
            .join(Users)
            .where(
                Subscriptions.stripe_subscription_id == sub_id,
                Subscriptions.user_id == Users.id,
                Users.stripe_customer_id == customer_id,
            )
        )
        return self.session.exec(stmt).first()

    def create(
        self,
        user_id: int,
        plan_id: int,
        subscription_id: str,
        status: str,
        current_period_end: datetime,
    ):
        new_susc = Subscriptions(
            user_id=user_id,
            plan_id=plan_id,
            stripe_subscription_id=subscription_id,
            status=status,
            current_period_end=current_period_end,
        )
        self.session.add(new_susc)
        self.session.commit()

    def update(
        self, id: str, status: Optional[str], current_period_end: Optional[datetime]
    ):
        sub_found = self.get_subscription_by_id(id)

        if status:
            sub_found.status = status

        if current_period_end:
            sub_found.current_period_end = current_period_end

        self.session.commit()

    def update_for_user(
        self,
        sub_id: str,
        customer_id: str,
        status: str,
        current_period_end: Optional[datetime],
    ):
        sub_found = self.get_subscription_for_user(sub_id, customer_id)

        if status:
            sub_found.status = status

        if current_period_end:
            sub_found.current_period_end = current_period_end

        self.session.commit()


def get_subs_repo(session: Session = Depends(get_session)):
    return SubscriptionRepository(session)

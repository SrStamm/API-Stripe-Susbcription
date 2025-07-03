from fastapi import Depends
from db.session import Session, get_session, select, SQLAlchemyError
from models.subscription import Subscriptions
from models.user import Users
from schemas.exceptions import DatabaseError
from typing import Optional
from datetime import datetime, timezone


class SubscriptionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_subscription_by_id(self, id: str):
        stmt = select(Subscriptions).where(Subscriptions.stripe_subscription_id == id)
        return self.session.exec(stmt).first()

    def get_all_subscription(self):
        stmt = select(Subscriptions)
        return self.session.exec(stmt).all()

    def get_all_subscription_by_user(self, user_id: int):
        stmt = select(Subscriptions).where(
            Subscriptions.is_active == True,
            Subscriptions.user_id == user_id,
        )
        return self.session.exec(stmt).all()

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
        try:
            new_susc = Subscriptions(
                user_id=user_id,
                plan_id=plan_id,
                stripe_subscription_id=subscription_id,
                status=status,
                current_period_end=current_period_end,
            )
            self.session.add(new_susc)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError(e, "SubscriptionRepository.create")

    def update(
        self, id: str, status: Optional[str], current_period_end: Optional[datetime]
    ):
        try:
            sub_found = self.get_subscription_by_id(id)

            if status:
                sub_found.status = status

            if current_period_end:
                sub_found.current_period_end = current_period_end

            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError(e, "SubscriptionRepository.update")

    def update_for_user(
        self,
        sub_id: str,
        customer_id: str,
        status: str,
        current_period_end: Optional[datetime],
        is_active: bool,
    ):
        try:
            sub_found = self.get_subscription_for_user(sub_id, customer_id)

            if status:
                sub_found.status = status

            if current_period_end:
                sub_found.current_period_end = current_period_end

            sub_found.is_active = is_active

            sub_found.updated_at = datetime.now(timezone.utc)

            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError(e, "SubscriptionRepository.update_for_user")

    def cancel(
        self, sub_id: str, customer_id: str, status: str, current_period_end: datetime
    ):
        try:
            sub_found = self.get_subscription_for_user(sub_id, customer_id)

            sub_found.status = status

            sub_found.current_period_end = current_period_end

            sub_found.is_active = False

            sub_found.canceled_at = datetime.now(timezone.utc)

            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError(e, "SubscriptionRepository.update_for_user")


def get_subs_repo(session: Session = Depends(get_session)):
    return SubscriptionRepository(session)

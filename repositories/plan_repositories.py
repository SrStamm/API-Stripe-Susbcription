from typing import Optional
from fastapi import Depends
from core.logger import logger
from models.plan import Plans
from db.session import SQLAlchemyError, get_session, Session, select
from schemas.enums import SubscriptionTier
from schemas.exceptions import DatabaseError, PlanNotFound


class PlanRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all_plans(self):
        stmt = select(Plans)
        return self.session.exec(stmt).all()

    def get_plan_by_id(self, id: str) -> Plans | None:
        stmt = select(Plans).where(Plans.stripe_price_id == id)
        return self.session.exec(stmt).first()

    def get_plan_by_plan_id(self, id: int) -> Plans | None:
        stmt = select(Plans).where(Plans.id == id)
        return self.session.exec(stmt).first()

    def get_plan_by_tier(self, tier: SubscriptionTier) -> Plans | None:
        stmt = select(Plans).where(Plans.name == tier.lower())
        return self.session.exec(stmt).first()

    def create(
        self,
        price_id: str,
        name: str,
        description: Optional[str],
        price_cents: int,
        interval: str,
    ):
        try:
            plan = Plans(
                stripe_price_id=price_id,
                name=name,
                description=description,
                price_cents=price_cents,
                interval=interval,
            )
            self.session.add(plan)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError(e, "PlanRepository.create")

    def update(
        self,
        old_price_id: str,
        new_price_id: str | None = None,
        price_cents: int | None = None,
        interval: str | None = None,
        name: str | None = None,
        description: str | None = None,
    ):
        try:
            old_product = self.get_plan_by_id(old_price_id)

            if not old_product:
                logger.warning(f"Product {old_price_id} not found")
                raise PlanNotFound(old_price_id)

            if new_price_id and price_cents and interval:
                old_product.price_cents = price_cents
                old_product.stripe_price_id = new_price_id
                old_product.interval = interval

            if name:
                old_product.name = name
            if description:
                old_product.description = description

            self.session.commit()
            self.session.refresh(old_product)
            return old_product

        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError(e, "PlanRepository.update")

    def delete(self, price_id: str):
        try:
            stmt = select(Plans).where(Plans.stripe_price_id == price_id)
            plans = self.session.exec(stmt).all()

            if plans:
                for plan in plans:
                    self.session.delete(plan)
                self.session.commit()
                return
            raise PlanNotFound(price_id)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError(e, "PlanRepository.delete")


def get_plan_repo(session: Session = Depends(get_session)):
    return PlanRepository(session)

from fastapi import Depends
from db.session import Session, get_session, select, SQLAlchemyError
from models.user import Users
from schemas.exceptions import DatabaseError


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user_by_email(self, email: str):
        stmt = select(Users).where(Users.email == email)
        return self.session.exec(stmt).first()

    def get_user_by_id(self, id: int):
        stmt = select(Users).where(Users.id == id)
        return self.session.exec(stmt).first()

    def get_user_by_customer_id(self, customer_id: str):
        stmt = select(Users).where(Users.stripe_customer_id == customer_id)
        return self.session.exec(stmt).first()

    def get_users(self):
        stmt = select(Users)
        return self.session.exec(stmt).all()

    def create(self, email: str):
        try:
            user = Users(email=email, stripe_customer_id=None)
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except SQLAlchemyError as e:
            raise DatabaseError(e, "UserRepository.create")

    def update(self, id: int, stripe_id: str):
        try:
            user = self.get_user_by_id(id)

            user.stripe_customer_id = stripe_id

            self.session.commit()
        except SQLAlchemyError as e:
            raise DatabaseError(e, "UserRepository.update")

    def delete(self, customer_id: str):
        try:
            user = self.get_user_by_customer_id(customer_id)
            self.session.delete(user)
            self.session.commit()
        except SQLAlchemyError as e:
            raise DatabaseError(e, "UserRepository.delete")


def get_user_repository(session: Session = Depends(get_session)) -> UserRepository:
    return UserRepository(session)

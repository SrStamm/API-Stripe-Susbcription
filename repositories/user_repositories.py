from fastapi import Depends
from db.session import Session, get_session, select
from models.user import ReadUser, Users


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, email: str):
        user = Users(email=email, stripe_customer_id=None)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_user_by_email(self, email: str):
        stmt = select(Users).where(Users.email == email)
        return self.session.exec(stmt).first()

    def get_user_by_id(self, id: int) -> ReadUser:
        stmt = select(Users).where(Users.id == id)
        return self.session.exec(stmt).first()

    def get_users(self):
        stmt = select(Users)
        return self.session.exec(stmt).all()

    def update(self, id: int, stripe_id: str):
        user = self.get_user_by_id(id)

        user.stripe_customer_id = stripe_id

        self.session.commit()


def get_user_repository(session: Session = Depends(get_session)) -> UserRepository:
    return UserRepository(session)

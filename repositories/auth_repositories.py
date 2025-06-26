from fastapi import Depends
from core.logger import logger
from db.session import Session, get_session, select, SQLAlchemyError
from sqlmodel import or_
from models.user import Users
from models.auth import Sessions
from datetime import datetime, timezone
from schemas.exceptions import DatabaseError


class AuthRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user_by_id(self, user_id: int):
        stmt = select(Users).where(Users.id == user_id)
        return self.session.exec(stmt).first()

    def get_user_whit_email(self, email: str):
        stmt = select(Users).where(Users.email == email)
        return self.session.exec(stmt).first()

    def new_session(self, jti: str, sub: str, expires_at: datetime):
        try:
            new_session = Sessions(jti=jti, sub=sub, expires_at=expires_at)
            self.session.add(new_session)
            self.session.commit()
            self.session.refresh(new_session)
            return new_session
        except SQLAlchemyError as e:
            logger.error(f"[AuthRepository.new_session] Database error: {e}")
            raise DatabaseError(e, "[AuthRepository.new_session]")

    def delete_session(self, actual_session: Sessions):
        self.session.delete(actual_session)
        self.session.commit()

    def get_session_with_jti(self, jti: str):
        stmt = select(Sessions).where(Sessions.jti == jti)
        return self.session.exec(stmt).first()

    def get_active_sessions(self, sub: str):
        stmt = select(Sessions).where(Sessions.sub == sub, Sessions.is_active == True)
        return self.session.exec(stmt).all()

    def get_expired_sessions(self):
        stmt = select(
            Sessions.sub,
            Sessions.is_active,
            Sessions.expires_at,
        ).where(
            or_(
                Sessions.is_active == False,
                Sessions.expires_at < datetime.now(timezone.utc),
            )
        )
        return self.session.exec(stmt).all()


def get_auth_repo(session: Session = Depends(get_session)):
    return AuthRepository(session)

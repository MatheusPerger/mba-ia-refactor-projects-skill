from sqlalchemy import func, select

from config.database import db
from models.user import User
from repositories.base import BaseRepository


class UserRepository(BaseRepository):
    model = User

    def list_all(self):
        return db.session.scalars(select(User).order_by(User.id)).all()

    def get_by_email(self, email):
        return db.session.scalar(select(User).where(User.email == email))

    def count(self):
        return db.session.scalar(select(func.count(User.id)))

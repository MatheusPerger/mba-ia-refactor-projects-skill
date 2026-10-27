from sqlalchemy import func, select

from config.database import db
from models.category import Category
from repositories.base import BaseRepository


class CategoryRepository(BaseRepository):
    model = Category

    def list_all(self):
        return db.session.scalars(select(Category).order_by(Category.id)).all()

    def count(self):
        return db.session.scalar(select(func.count(Category.id)))

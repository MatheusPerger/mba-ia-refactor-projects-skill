from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from config.constants import FINISHED_STATUSES, STATUS_DONE
from config.database import db
from models.task import Task
from repositories.base import BaseRepository


class TaskRepository(BaseRepository):
    model = Task

    def list_all_with_relations(self):
        stmt = select(Task).options(joinedload(Task.user), joinedload(Task.category)).order_by(Task.id)
        return db.session.scalars(stmt).unique().all()

    def list_by_user(self, user_id):
        stmt = select(Task).where(Task.user_id == user_id).order_by(Task.id)
        return db.session.scalars(stmt).all()

    def search(self, text=None, status=None, priority=None, user_id=None):
        stmt = select(Task)
        if text:
            stmt = stmt.where(or_(Task.title.like(f'%{text}%'), Task.description.like(f'%{text}%')))
        if status:
            stmt = stmt.where(Task.status == status)
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)
        if user_id is not None:
            stmt = stmt.where(Task.user_id == user_id)
        return db.session.scalars(stmt.order_by(Task.id)).all()

    def count(self):
        return db.session.scalar(select(func.count(Task.id)))

    def count_by_status(self):
        rows = db.session.execute(select(Task.status, func.count(Task.id)).group_by(Task.status)).all()
        return dict(rows)

    def count_by_priority(self):
        rows = db.session.execute(select(Task.priority, func.count(Task.id)).group_by(Task.priority)).all()
        return dict(rows)

    def count_by_user(self):
        rows = db.session.execute(
            select(Task.user_id, func.count(Task.id)).where(Task.user_id.is_not(None)).group_by(Task.user_id)
        ).all()
        return dict(rows)

    def count_done_by_user(self):
        rows = db.session.execute(
            select(Task.user_id, func.count(Task.id))
            .where(Task.user_id.is_not(None), Task.status == STATUS_DONE)
            .group_by(Task.user_id)
        ).all()
        return dict(rows)

    def count_by_category(self):
        rows = db.session.execute(
            select(Task.category_id, func.count(Task.id)).where(Task.category_id.is_not(None)).group_by(Task.category_id)
        ).all()
        return dict(rows)

    def overdue(self, now):
        stmt = select(Task).where(
            Task.due_date.is_not(None), Task.due_date < now, Task.status.not_in(FINISHED_STATUSES)
        ).order_by(Task.id)
        return db.session.scalars(stmt).all()

    def count_created_since(self, since):
        return db.session.scalar(select(func.count(Task.id)).where(Task.created_at >= since))

    def count_done_updated_since(self, since):
        return db.session.scalar(
            select(func.count(Task.id)).where(Task.status == STATUS_DONE, Task.updated_at >= since)
        )

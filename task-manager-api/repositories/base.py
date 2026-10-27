import logging

from sqlalchemy.exc import SQLAlchemyError

from config.database import db
from utils.errors import PersistenceError

logger = logging.getLogger(__name__)


class BaseRepository:
    model = None

    def get(self, entity_id):
        return db.session.get(self.model, entity_id)

    def add(self, entity):
        db.session.add(entity)

    def delete(self, entity):
        db.session.delete(entity)

    def commit(self, error_message):
        try:
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            logger.exception('Falha ao gravar: %s', error_message)
            raise PersistenceError(error_message) from exc

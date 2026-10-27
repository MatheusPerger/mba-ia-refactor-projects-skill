import hashlib
import hmac
import re

from werkzeug.security import check_password_hash, generate_password_hash

from config.constants import ROLE_ADMIN, ROLE_USER
from config.database import db
from utils.clock import utc_now

LEGACY_MD5_PATTERN = re.compile(r'[0-9a-f]{32}')


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=ROLE_USER)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def uses_legacy_hash(self):
        """Senhas gravadas antes da migração são MD5 puro (32 hex)."""
        return bool(LEGACY_MD5_PATTERN.fullmatch(self.password or ''))

    def check_password(self, pwd):
        if self.uses_legacy_hash():
            return hmac.compare_digest(self.password, hashlib.md5(pwd.encode()).hexdigest())
        return check_password_hash(self.password, pwd)

    def is_admin(self):
        return self.role == ROLE_ADMIN

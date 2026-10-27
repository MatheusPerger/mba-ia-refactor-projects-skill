from datetime import datetime

from config.constants import (
    DATE_FORMAT, EMAIL_PATTERN, MAX_PRIORITY, MAX_TITLE_LENGTH, MIN_PASSWORD_LENGTH,
    MIN_PRIORITY, MIN_TITLE_LENGTH, VALID_ROLES, VALID_STATUSES,
)
from utils.errors import ValidationError


def ensure_payload(data):
    if not data or not isinstance(data, dict):
        raise ValidationError('Dados inválidos')
    return data


def ensure_title(title):
    if not isinstance(title, str):
        raise ValidationError('Título inválido')
    if len(title) < MIN_TITLE_LENGTH:
        raise ValidationError('Título muito curto')
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError('Título muito longo')
    return title


def ensure_status(status):
    if status not in VALID_STATUSES:
        raise ValidationError('Status inválido')
    return status


def ensure_priority(priority):
    is_number = isinstance(priority, int) and not isinstance(priority, bool)
    if not is_number or priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise ValidationError(f'Prioridade deve ser entre {MIN_PRIORITY} e {MAX_PRIORITY}')
    return priority


def parse_due_date(value, error_message):
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except (TypeError, ValueError):
        raise ValidationError(error_message)


def normalize_tags(tags):
    if isinstance(tags, list):
        if not all(isinstance(tag, str) for tag in tags):
            raise ValidationError('Tags inválidas')
        return ','.join(tags)
    return tags


def ensure_email(email):
    if not isinstance(email, str) or not EMAIL_PATTERN.match(email):
        raise ValidationError('Email inválido')
    return email


def ensure_password(password, too_short_message):
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(too_short_message)
    return password


def ensure_role(role):
    if role not in VALID_ROLES:
        raise ValidationError('Role inválido')
    return role


def parse_int_param(value, name):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError(f'Parâmetro {name} inválido')

from datetime import datetime, timezone


def utc_now():
    """UTC atual como datetime naive, o mesmo formato gravado no banco."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

from dataclasses import field

from datetime import datetime, timezone


def default(fn):
    return field(default_factory=fn)


def now():
    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()

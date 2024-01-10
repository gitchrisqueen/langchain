import dateparser
import dateutil.parser as isoparser
from datetime import datetime
from dateutil.tz import UTC


def get_datetime(text: str) -> datetime:
    dt = dateparser.parse(text)
    if dt is None:
        raise ValueError("invalid datetime as string")

    return dt


def get_iso_date(text: str) -> datetime:
    # Convert the string into a datetime string
    date_time = get_datetime(text)
    # Return the ISO
    return isoparser.parse(date_time.strftime("%Y-%m-%d")).astimezone(UTC)


def get_iso_date_string(text: str) -> str:
    return get_iso_date(text).isoformat()

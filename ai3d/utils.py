import pytz
import json

from datetime import datetime
from uuid import UUID

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def convert_timezone(dt: datetime, tz: str = "Europe/Berlin") -> datetime:
    """Converts a datetime object to the specified timezone — naive -> aware

    Parameters
    ----------
    dt : datetime.datetime
        The datetime object to convert
    tz : str
        The timezone to convert to

    Returns
    -------
    datetime.datetime
        The converted datetime object
    """
    return dt.astimezone(pytz.timezone(tz))


def datetime_now() -> datetime:
    """Returns the current datetime object

    Returns
    -------
    datetime.datetime
        The current datetime object
    """
    return convert_timezone(datetime.now())


def jsonify(response: str) -> dict | str:
    """Converts a string response to a dict

    Parameters
    ----------
    response : str
        The response to convert

    Returns
    -------
    dict
        The converted response
    """
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        pass
    finally:
        return response


def flatten_messages(messages: list[str]) -> str:
    """Flattens a list of messages to a single string

    Parameters
    ----------
    messages : list[str]
        The messages to flatten

    Returns
    -------
    str
        The flattened messages
    """
    return "\n\n".join(messages)


async def uuid_to_str(id: UUID) -> str:
    """Converts a UUID to a string

    Parameters
    ----------
    id : UUID
        The UUID to convert

    Returns
    -------
    str
        The converted UUID
    """
    return str(id)


async def interaction_id_to_str(interaction_id: UUID) -> str:
    """Converts a UUID to a string

    Parameters
    ----------
    interaction_id : UUID
        The UUID to convert

    Returns
    -------
    str
        The converted UUID
    """
    return str(interaction_id)


def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)

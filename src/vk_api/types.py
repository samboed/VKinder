import dataclasses
from collections import namedtuple
from enum import Enum, StrEnum


User = namedtuple('User',
                  ["id", "first_name", "last_name", "city", "bdate", "sex_index", "is_closed"],
                  defaults='')


Attachment = namedtuple('Attachment',
                        ["type", "owner_id", "media_id"],
                        defaults='')


Photo = namedtuple('Photo',["attachment", "like_count"])


EventAnswer = namedtuple('Event', ["user_id", "event_id", "peer_id"])


Region = namedtuple("Region", ["id", "name"])


City = namedtuple("City", ["id", "name", "area", "region"], defaults='')


class Events(Enum):
    SEND_MESSAGE = 1
    PUSH_BUTTON = 2


class Sex(Enum):
    any = 0
    women = 1
    men = 2


@dataclasses.dataclass(frozen=True)
class ButtonTypes(StrEnum):
    text = "text"
    location = "location"
    open_link = "open_link"
    callback = "callback"


@dataclasses.dataclass(frozen=True)
class ButtonColorTypes(StrEnum):
    primary = "primary"
    secondary = "secondary"
    negative = "negative"
    positive = "positive"


def get_attachment_photo(user_id: int, media_id: int):
    return Attachment("photo", user_id, media_id)

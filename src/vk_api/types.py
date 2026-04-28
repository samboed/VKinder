import dataclasses
from collections import namedtuple
from enum import Enum, StrEnum


User = namedtuple('User',
                  ["id", "first_name", "last_name", "city", "bdate",
                   "sex_index", "relation_index", "is_closed"],
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
    ANY = 0
    WOMEN = 1
    MEN = 2


class Relation(Enum):
    NOT_MARRIED = 1
    HAVE_SWEETHEART = 2
    ENGAGED = 3
    MARRIED = 4
    COMPLICATED = 5
    IN_ACTIVE_SEARCHING = 6
    IN_LOVE = 7
    CMN_LAW_MARRIAGE = 8


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


def get_attachment_photo(owner_id: int, media_id: int) -> Attachment:
    return Attachment("photo", owner_id, media_id)

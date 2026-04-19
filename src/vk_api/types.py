import dataclasses
from collections import namedtuple
from enum import Enum, StrEnum


Attachment = namedtuple('Attachment',
                        ["type", "owner_id", "media_id", "access_key"],
                        defaults=None)


Photo = namedtuple('Photo',
                          ["attachment", "like_count"])


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

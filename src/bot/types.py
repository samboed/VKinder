from collections import namedtuple
from enum import IntEnum


Location = namedtuple("Location",
                      ["city_id", "city_name", "region_id", "region_name"],
                      defaults='')


class DialogStates(IntEnum):
    INITIAL = 0
    SETUP_REGION = 1
    SETUP_CITY = 2
    SETUP_AGE_FROM = 3
    SETUP_AGE_TO = 4
    SHOW_FAVORITE_PHOTO = 5
    SHOW_BLACKLIST_PERSON_PHOTO = 6
    DEL_FAVORITE = 7
    DEL_BLACKLIST_PERSON = 8

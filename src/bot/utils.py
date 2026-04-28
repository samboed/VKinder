from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_full_age(bdate: str) -> int | bool:
    try:
        current_time = datetime.now()
        user_birthday_datetime = datetime.strptime(bdate, "%d.%m.%Y")
        full_age = relativedelta(current_time, user_birthday_datetime).years
    except ValueError:
        return False

    return full_age
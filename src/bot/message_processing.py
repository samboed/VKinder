from src.bot.base import BotBase
from src.bot.constants import AGE_MIN_SEARCHING, AGE_MAX_SEARCHING


class BotMessage(BotBase):
    def __init__(self, group_token, user_token, group_id):
        super().__init__(group_token, user_token, group_id)

    def _process_age_from_message(self, user_id: int, message: str, comment: str):
        filtered_message = message.strip()
        if filtered_message.isdigit():
            age = int(filtered_message)
            if age < AGE_MIN_SEARCHING:
                warn_message = (f"Указан неверный {comment}. Возраст должен быть больше {AGE_MIN_SEARCHING} лет. "
                                f"Попробуйте ещё раз❗")
                self._api.send_message(user_id, warn_message)
                return False
            elif age > AGE_MAX_SEARCHING:
                warn_message = (f"Указан неверный {comment}. Возраст должен быть меньше {AGE_MAX_SEARCHING} лет. "
                                f"Попробуйте ещё раз❗")
                self._api.send_message(user_id, warn_message)
                return False
        else:
            self._api.send_message(user_id, f"Указан неверный {comment}. Возраст должен быть указан числом. "
                                             f"Попробуйте ещё раз❗")
            return False

        return age

    def _process_digit_from_message(self, user_id: int, message: str, comment: str):
        filtered_message = message.strip()
        if not filtered_message.isdigit():
            self._api.send_message(user_id, f"Указан неверный {comment}. "
                                             f"Порядковый номер должен быть указан числом. "
                                             f"Попробуйте ещё раз❗")
            return False
        return filtered_message

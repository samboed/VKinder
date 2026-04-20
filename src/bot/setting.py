from datetime import datetime

from dateutil.relativedelta import relativedelta

from src.bot.base import BotBase
from src.bot.constants import AGE_MIN_SEARCHING, AGE_DEF_MAX_SEARCHING
from src.bot.formatters import get_sex_str, get_age_range_str, get_location_str
from src.bot.message_processing import BotMessage


class BotSetting(BotMessage, BotBase):
    def __init__(self, group_token, user_token, group_id):
        super().__init__(group_token, user_token, group_id)

    def _setup_and_show_init_settings(self, user_id: int):
        user_data = self._api.get_info_about_user(user_id)

        cities = self._api.get_cities(city_name=user_data.city.name, region_id=user_data.city.id)

        target_city = cities[0]

        setup_region_id = target_city.id
        setup_region_name = target_city.region
        setup_city_id = user_data.city.id
        setup_city_name = user_data.city.name
        setup_sex = user_data.sex_index % 2 + 1

        try:
            current_time = datetime.now()
            user_birthday_datetime = datetime.strptime(user_data.bdate, "%d.%m.%Y")
            full_user_years = relativedelta(current_time, user_birthday_datetime).years

            setup_age_from = full_user_years
            setup_age_to = full_user_years
        except ValueError:
            setup_age_from = AGE_MIN_SEARCHING
            setup_age_to = AGE_DEF_MAX_SEARCHING

        self.db.get_or_create_region(setup_region_id, setup_region_name)
        self.db.get_or_create_city(setup_city_id, setup_city_name, setup_region_id)

        self.db.update_user_setting(
            user_id,
            city_id=setup_city_id,
            sex_index=setup_sex,
            age_from=setup_age_from,
            age_to=setup_age_to
        )

        sex_name = get_sex_str(setup_sex)
        age_info = get_age_range_str(setup_age_from, setup_age_to)
        location_info = get_location_str(setup_city_name, setup_region_name)

        info_text = (f"Были установлены следующие настройки для поиска 🔍\n"
                     f"Город: {location_info}\n"
                     f"Пол: {sex_name}\n"
                     f"Возраст: {age_info}")

        self._api.send_message(user_id, info_text)

    def _setup_sex(self, user_id: int, sex_index: int):
        self.db.update_user_setting(user_id, sex_index=sex_index)

        sex_name = get_sex_str(sex_index)
        self._api.send_message(user_id, f"Был установлен пол для поиска - {sex_name}")

    def _setup_region(self, user_id: int, message: str):
        regions = self._api.get_regions(message)
        if not regions:
            self._api.send_message(user_id, f"Региона с названием '{message}' не было найдено в базе. "
                                            f"Попробуйте ещё раз, переформулировав название❗")
            return False

        region = regions[0]

        self.db.get_or_create_region(region.id, region.name)
        self.db.update_temp_setting(user_id, region_id=region.id)

        self._api.send_message(user_id, f"Для поиска был установлен регион {region.name} ✅")

        return True

    def _setup_city(self, user_id: int, message: str):
        temp_settings = self.db.get_temp_setting(user_id)
        region_id = temp_settings.region_id if temp_settings else None

        cities = self._api.get_cities(message, region_id)
        if not cities:
            self._api.send_message(user_id, f"Города с названием '{message}' не было найдено в базе. "
                                            f"Попробуйте ещё раз, переформулировав название❗")
            return False

        city = cities[0]

        self.db.get_or_create_city(city.id, city.name, region_id)
        self.db.update_user_setting(user_id, city_id=city.id)

        self._api.send_message(user_id, f"Для поиска был установлен город {city.name} ✅")

        return True

    def _setup_age_from(self, user_id: int, message: str):
        comment = "минимальный возраст"

        age = self._process_age_from_message(user_id, message, comment)

        if not age:
            return False

        self.db.update_temp_setting(user_id, age_from=age)

        self._api.send_message(user_id, f"Был установлен {comment} {age} для поиска ✅")

        return True

    def _setup_age_to(self, user_id: int, message: str):
        comment = "максимальный возраст"

        age = self._process_age_from_message(user_id, message, comment)

        if not age:
            return False

        temp_settings = self.db.get_temp_setting(user_id)
        age_from = temp_settings.age_from if temp_settings and temp_settings.age_from else AGE_MIN_SEARCHING

        if age_from > age:
            warn_message = (f"Указан неверный {comment}. "
                            f"Возраст {age} не может быть меньше минимального {age_from}")
            self._api.send_message(user_id, warn_message)
            return False

        self.db.update_user_setting(user_id, age_from=age_from, age_to=age)

        self._api.send_message(user_id, f"Был установлен {comment} {age} для поиска ✅")

        return True

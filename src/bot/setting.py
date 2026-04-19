from datetime import datetime
from dateutil.relativedelta import relativedelta

from src.bot.base import BotBase
from src.bot.formatters import get_sex_str, get_age_range_str, get_location_str
from src.bot.message_processing import BotMessage
from src.bot.constants import AGE_MIN_SEARCHING, AGE_DEF_MAX_SEARCHING

import src.bot.testing as testing # TODO: for testing


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
            full_user_years = relativedelta(current_time, user_birthday_datetime).year

            setup_age_from = full_user_years
            setup_age_to = full_user_years
        except ValueError:
            setup_age_from = AGE_MIN_SEARCHING
            setup_age_to = AGE_DEF_MAX_SEARCHING

        # TODO: save user in Users table
        is_new_user = testing.is_new_user = False # TODO: for testing

        # TODO: save setup_city_id, setup_city_name, setup_sex, setup_age_from, setup_age_to in Preferences table
        region_id = testing.region_id = setup_region_id # TODO: for testing
        region_name = testing.region_name = setup_region_name # TODO: for testing
        city_id = testing.city_id = setup_city_id # TODO: for testing
        city_name = testing.city_name = setup_city_name # TODO: for testing
        sex_ind = testing.sex_ind = setup_sex # TODO: for testing
        age_from = testing.age_from = setup_age_from # TODO: for testing
        age_to = testing.age_to = setup_age_to # TODO: for testing

        sex_name = get_sex_str(setup_sex)
        age_info = get_age_range_str(age_from, age_to)
        location_info = get_location_str(city_name, region_name)

        info_text = (f"Были установлены следующие настройки для поиска 🔍\n"
                     f"Город: {location_info}\n"
                     f"Пол: {sex_name}\n"
                     f"Возраст: {age_info}")

        self._api.send_message(user_id, info_text)

    def _setup_sex(self, user_id: int, sex_index: int):
        # TODO: add sex preference to UserPreferences table
        global sex_ind # TODO: for testing
        testing.sex_ind = sex_index # TODO: for testing

        sex_name = get_sex_str(sex_index)

        self._api.send_message(user_id, f"Был установлен пол для поиска - {sex_name}")

    def _setup_region(self, user_id: int, message: str):
        regions = self._api.get_regions(message)
        if not regions:
            self._api.send_message(user_id, f"Региона с названием '{message}' не было найдено в базе. "
                                            f"Попробуйте ещё раз, переформулировав название❗")
            return False

        region = regions[0]

        # TODO: save region info in temp Settings table (region_name, region_id)
        global region_name, reg_id  # TODO: for testing
        testing.region_name = region.name  # TODO: for testing
        testing.reg_id = region.id  # TODO: for testing
        ###

        self._api.send_message(user_id, f"Для поиска был установлен регион {region.name} ✅")

        return True

    def _setup_city(self, user_id: int, message: str):
        # TODO: get from db region_id
        region_id = testing.reg_id  # TODO: for testing
        ###

        cities = self._api.get_cities(message, region_id)
        if not cities:
            self._api.send_message(user_id, f"Города с названием '{message}' не было найдено в базе. "
                                             f"Попробуйте ещё раз, переформулировав название❗")
            return False

        city = cities[0]
        # TODO: save city info in Preferences (city.id, city.name) and region info from temp Settings table (region_id, region_name)
        global city_name  # TODO: for testing
        testing.city_name = city.name  # TODO: for testing
        testing.city_id = city.id  # TODO: for testing

        self._api.send_message(user_id, f"Для поиска был установлен город {city.name} ✅")

        return True

    def _setup_age_from(self, user_id: int, message: str):
        comment = "минимальный возраст"

        age = self._process_age_from_message(user_id, message, comment)

        if not age:
            return False

        # TODO: save age_from in TempSettings table
        global age_from  # TODO: for testing
        testing.age_from = age  # TODO: for testing

        self._api.send_message(user_id, f"Был установлен {comment} {age} для поиска ✅")

        return True

    def _setup_age_to(self, user_id: int, message: str):
        comment = "максимальный возраст"

        age = self._process_age_from_message(user_id, message, comment)

        if not age:
            return False

        # TODO: get 'age_from' from TempSettings table
        age_from = testing.age_from # TODO: for testing

        if  age_from > age:
            warn_message = (f"Указан неверный {comment}. "
                            f"Возраст {age} не может быть меньше минимального {age_from}")
            self._api.send_message(user_id, warn_message)
            return False

        # TODO: save age_to and age_from in Preferences table
        global age_to  # TODO: for testing
        testing.age_to = age  # TODO: for testing

        self._api.send_message(user_id, f"Был установлен {comment} {age} для поиска ✅")

        return True

from src.bot.utils import get_full_age
from src.bot.base import BotBase
from src.bot.constants import AGE_MIN_SEARCHING, AGE_DEF_MAX_SEARCHING
from src.bot.formatters import get_sex_str, get_age_range_str, get_location_str
from src.bot.message_processing import BotMessage


class BotSetting(BotMessage, BotBase):
    def __init__(self, group_token, user_token, group_id, engine):
        super().__init__(group_token, user_token, group_id, engine)

    def _setup_and_show_init_settings(self, user_id: int) -> bool:
        get_user_data = self._api.get_info_about_user(user_id)
        if not get_user_data:
            self._api.send_message(user_id, "Не удалось получить стандартные настройки для поиска. "
                                            "Попробуйте перезапустить бота! 🤖")
            return False

        user_data = get_user_data

        if not user_data.city.id:
            setup_city_id = 1
            setup_city_name = "Москва"
        else:
            setup_city_id = user_data.city.id
            setup_city_name = user_data.city.name

        setup_region_id = None
        setup_region_name = ''

        res_get_cities = self._api.get_cities(city_name=setup_city_name)
        if res_get_cities is False:
            self._api.send_message(user_id, "Не удалось получить данные о городе. "
                                            "Попробуйте перезапустить бота! 🤖")
            return False
        elif res_get_cities:
            target_city = res_get_cities[0]
            region_name = target_city.region

            if region_name:
                res_get_region = self._api.get_regions(region_name)[0]
                if res_get_region is False:
                    return False
                elif res_get_region:
                    region = res_get_region

                    setup_region_id = region.id
                    setup_region_name = region.name


        setup_sex = user_data.sex_index % 2 + 1

        user_age = get_full_age(user_data.bdate)
        if user_age:
            setup_age_from = user_age
            setup_age_to = user_age
        else:
            setup_age_from = AGE_MIN_SEARCHING
            setup_age_to = AGE_DEF_MAX_SEARCHING

        if setup_region_id:
            self._db.add_region(setup_region_id, setup_region_name)

        self._db.add_city(setup_city_id, setup_city_name)

        self._db.update_user_setting(user_id,
                                     city_id=setup_city_id,
                                     sex_index=setup_sex,
                                     age_from=setup_age_from,
                                     age_to=setup_age_to)

        location_info = get_location_str(setup_city_name, setup_region_name)
        sex_name = get_sex_str(setup_sex)
        age_info = get_age_range_str(setup_age_from, setup_age_to)

        info_text = (f"Были установлены следующие настройки для поиска 🔍\n"
                     f"Город: {location_info}\n"
                     f"Пол: {sex_name}\n"
                     f"Возраст: {age_info}")

        self._api.send_message(user_id, info_text)

        return True

    def _setup_sex(self, user_id: int, sex_index: int):
        self._db.update_user_setting(user_id, sex_index=sex_index)

        sex_name = get_sex_str(sex_index)
        self._api.send_message(user_id, f"Был установлен пол для поиска - {sex_name}")

    def _setup_region(self, user_id: int, message: str):
        res_get_regions = self._api.get_regions(message)
        if res_get_regions is False:
            self._api.send_message(user_id, "Не получилось найти региона в базе. "
                                            "Попробуйте ещё раз❗")
            return False
        elif not res_get_regions:
            self._api.send_message(user_id, f"Региона с названием '{message}' не было найдено в базе. "
                                            f"Попробуйте ещё раз, переформулировав название❗")
            return False

        target_region = res_get_regions[0]

        if not self._db.get_region(target_region.id):
            self._db.add_region(target_region.id, target_region.name)

        self._db.update_temp_setting(user_id, region_id=target_region.id)

        self._api.send_message(user_id, f"Был сохранён регион {target_region.name}, "
                                        f"чтобы его использовать в поиске, необходимо "
                                        f"указать город 💾")

        return True

    def _setup_city(self, user_id: int, message: str):
        temp_settings = self._db.get_temp_setting(user_id)

        region = self._db.get_region(temp_settings.region_id)
        if not region:
            res_get_cities = self._api.get_cities(message)
            region_name = ''
        else:
            res_get_cities = self._api.get_cities(message, region.region_id)
            region_name = region.name

        if res_get_cities is False:
            self._api.send_message(user_id, "Не получилось найти города в базе. "
                                            "Попробуйте ещё раз❗")
            return False
        elif not res_get_cities:
            self._api.send_message(user_id, f"Города с названием '{message}' не было найдено в базе. "
                                            f"Попробуйте ещё раз, переформулировав название❗")
            return False

        target_city = res_get_cities[0]

        if not self._db.get_city(target_city.id):
            self._db.add_city(target_city.id, target_city.name)

        self._db.update_user_setting(user_id, city_id=target_city.id, region_id=region.region_id)

        location = get_location_str(target_city.name, region_name)

        self._api.send_message(user_id, f"Для поиска был установлен {location} ✅")

        return True

    def _setup_age_from(self, user_id: int, message: str):
        comment = "минимальный возраст"

        age = self._process_age_from_message(user_id, message, comment)

        if not age:
            return False

        self._db.update_temp_setting(user_id, age_from=age)

        self._api.send_message(user_id, f"Был сохранён {comment} {age}, "
                                        f"чтобы его использовать в поиске необходимо, "
                                        f"указать максимальный возраст 💾")

        return True

    def _setup_age_to(self, user_id: int, message: str):
        comment_age_from = "минимальный возраст"
        comment_age_to = "максимальный возраст"

        age = self._process_age_from_message(user_id, message, comment_age_to)

        if not age:
            return False

        temp_settings = self._db.get_temp_setting(user_id)

        age_from = AGE_MIN_SEARCHING
        if temp_settings:
            age_from = temp_settings.age_from

        if age_from > age:
            warn_message = (f"Указан неверный {comment_age_to}. "
                            f"Возраст {age} не может быть меньше минимального {age_from}❗")
            self._api.send_message(user_id, warn_message)
            return False

        self._db.update_user_setting(user_id, age_from=age_from, age_to=age)

        self._api.send_message(user_id, f"Были установлены {comment_age_from} {age_from} "
                                        f"и {comment_age_to} {age} для поиска ✅")

        return True

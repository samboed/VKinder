from src.bot.base import BotBase
from src.bot.formatters import get_user_info_str, get_sex_str, get_age_range_str, get_location_str
from src.bot.keyboard import (main_menu_keyboard, favorites_keyboard, blacklist_keyboard,
                              settings_menu_keyboard, sex_setting_keyboard)
from src.bot.message_processing import BotMessage
from src.bot.message_texts import (MAIN_MENU_TEXT, SPECIFY_REGION_TEXT,
                                   SPECIFY_CITY_TEXT, SELECT_SEX_TEXT,
                                   SPECIFY_AGE_FROM_TEXT, SPECIFY_AGE_TO_TEXT)
from src.bot.partner import BotPartner


class BotShow(BotPartner, BotMessage, BotBase):
    def __init__(self, group_token, user_token, group_id):
        super().__init__(group_token, user_token, group_id)

    def _show_main_menu(self, user_id: int):
        self._api.send_message(user_id, MAIN_MENU_TEXT, main_menu_keyboard)

    def __show_partner_photos(self, user_id: int, message: str, comment: str, get_list_func):
        favorite_num = self._process_digit_from_message(user_id, message, comment)

        if not favorite_num:
            return False

        people_list = get_list_func(user_id)

        if favorite_num < 1 or favorite_num > len(people_list):
            self._api.send_message(user_id, "Пользователя с таким номером нет в списке❗")
            return False

        candidate = people_list[favorite_num - 1]

        user_info = get_user_info_str(candidate.vk_id,
                                      candidate.first_name,
                                      candidate.last_name,
                                      city_name="",
                                      region_name="")

        photo_attachments = [photo.url for photo in candidate.photos]

        self._api.send_message(user_id, user_info, attachments=photo_attachments)

        return True

    def _show_favorite_photos(self, user_id: int, message: str):
        comment = "порядковый номер профиля из избранных"
        return self.__show_partner_photos(user_id, message, comment, self.db.get_favorites)

    def _show_blacklist_person_photos(self, user_id: int, message: str):
        comment = "порядковый номер профиля из блэклиста"
        return self.__show_partner_photos(user_id, message, comment, self.db.get_blacklist)

    def _show_favorites(self, user_id: int):
        favorites_info = self._get_general_people_info_from_favorites(user_id)
        self._api.send_message(user_id, favorites_info,
                               favorites_keyboard)

    def _show_blacklist(self, user_id: int):
        blacklist_info = self._get_general_people_info_from_blacklist(user_id)
        self._api.send_message(user_id, blacklist_info,
                               blacklist_keyboard)

    def _show_settings(self, user_id: int):
        settings = self.db.get_user_settings(user_id)

        if settings:
            city_name = settings.city_name or ""
            region_name = settings.region_name or ""
            sex_index = settings.sex_index or 0
            age_from = settings.age_from or 0
            age_to = settings.age_to or 0
        else:
            city_name, region_name, sex_index, age_from, age_to = ("", "", 0, 0, 0)

        sex_name = get_sex_str(sex_index)
        age_info = get_age_range_str(age_from, age_to)
        location_info = get_location_str(city_name, region_name)

        info_text = (f"Настройки для поиска 🔍\n"
                     f"Город: {location_info}\n"
                     f"Пол: {sex_name}\n"
                     f"Возраст: {age_info}")

        self._api.send_message(user_id, info_text, settings_menu_keyboard)

    def _show_region_setup(self, user_id: int):
        self._api.send_message(user_id, SPECIFY_REGION_TEXT)

    def _show_city_setup(self, user_id: int):
        self._api.send_message(user_id, SPECIFY_CITY_TEXT)

    def _show_sex_setup(self, user_id: int):
        self._api.send_message(user_id, SELECT_SEX_TEXT, sex_setting_keyboard)

    def _show_age_from_setting(self, user_id: int):
        self._api.send_message(user_id, SPECIFY_AGE_FROM_TEXT)

    def _show_age_to_setting(self, user_id: int):
        self._api.send_message(user_id, SPECIFY_AGE_TO_TEXT)

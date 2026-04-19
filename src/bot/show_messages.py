from src.bot.base import BotBase
from src.bot.formatters import get_user_info_str, get_sex_str, get_age_range_str, get_location_str
from src.bot.keyboard import (main_menu_keyboard, favorites_keyboard, blacklist_keyboard,
                              settings_menu_keyboard, sex_setting_keyboard)
from src.bot.message_processing import BotMessage
from src.bot.message_texts import (MAIN_MENU_TEXT, SPECIFY_REGION_TEXT,
                                   SPECIFY_CITY_TEXT, SELECT_SEX_TEXT,
                                   SPECIFY_AGE_FROM_TEXT, SPECIFY_AGE_TO_TEXT)
from src.bot.partner import BotPartner


import src.bot.testing as testing # TODO: for testing


class BotShow(BotPartner, BotMessage, BotBase):
    def __init__(self, group_token, user_token, group_id):
        super().__init__(group_token, user_token, group_id)

    def _show_main_menu(self, user_id: int):
        self._api.send_message(user_id, MAIN_MENU_TEXT, main_menu_keyboard)

    def __show_partner_photos(self, user_id: int, message: str, comment: str):
        favorite_num = self._process_digit_from_message(user_id, message, comment)

        if not favorite_num:
            return False

        # TODO: get favorite_id, first_name, last_name, city_name, region_name from Favorites
        # favorite_id, favorite_first_name, favorite_last_name, city_name, region_name = get_from_db(favorite_num)
        partner_id = 1  # TODO: for testing
        partner_first_name = "First Name"  # TODO: for testing
        partner_last_name = "Last Name"  # TODO: for testing
        partner_city_name = "Test City"  # TODO: for testing
        partner_region_name = "Test Region"  # TODO: for testing

        media_id_list = []  # TODO: for testing, get from db by favorite_id

        user_info = get_user_info_str(partner_id,
                                      partner_first_name,
                                      partner_last_name,
                                      partner_city_name,
                                      partner_region_name)

        photo_attachments = []
        for media_id in media_id_list:
            photo_attachments.append(self._api.get_attachment_photo(partner_id, media_id))

        self._api.send_message(user_id, user_info, attachments=photo_attachments)

        return True

    def _show_favorite_photos(self, user_id: int, message: str):
        comment = "порядковый номер профиля из избранных"

        return self.__show_partner_photos(user_id, message, comment)

    def _show_blacklist_person_photos(self, user_id: int, message: str):
        comment = "порядковый номер профиля из блэклиста"

        return self.__show_partner_photos(user_id, message, comment)

    def _show_favorites(self, user_id: int):
        favorites_info = self._get_general_people_info_from_favorites(user_id)
        self._api.send_message(user_id, favorites_info,
                                favorites_keyboard)

    def _show_blacklist(self, user_id: int):
        blacklist_info = self._get_general_people_info_from_blacklist(user_id)
        self._api.send_message(user_id, blacklist_info,
                                blacklist_keyboard)

    def _show_settings(self, user_id: int):
        # TODO: get preference data from table UserPreferences
        # city_name, region_name, sex_index, age_from, age_to = get_from_db_func(user_id) # TODO: insert your realization
        ###

        city_name = testing.city_name # TODO: for testing
        region_name = testing.region_name # TODO: for testing
        sex_index = testing.sex_ind # TODO: for testing
        age_from = testing.age_from # TODO: for testing
        age_to = testing.age_to # TODO: for testing

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

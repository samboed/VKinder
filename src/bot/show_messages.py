from sqlalchemy.engine.base import Engine

from src.bot.base import BotBase
from src.bot.formatters import get_user_info_str, get_sex_str, get_age_range_str, get_location_str
from src.bot.keyboard import (main_menu_keyboard, favorites_keyboard, blacklist_keyboard,
                              settings_menu_keyboard, sex_setting_keyboard)
from src.bot.message_processing import BotMessage
from src.bot.message_texts import (MAIN_MENU_TEXT, SPECIFY_REGION_TEXT,
                                   SPECIFY_CITY_TEXT, SELECT_SEX_TEXT,
                                   SPECIFY_AGE_FROM_TEXT, SPECIFY_AGE_TO_TEXT)
from src.bot.partner import BotPartner
from src.vk_api.types import get_attachment_photo


class BotShow(BotPartner, BotMessage, BotBase):
    def __init__(self, group_token: str, group_id: int,
                 user_token: str, engine: Engine):
        super().__init__(group_token, group_id, user_token, engine)

    def _show_main_menu(self, user_id: int):
        self._api.send_message(user_id, MAIN_MENU_TEXT, main_menu_keyboard)

    def __show_partner_photos(self, user_id: int, message: str,
                              comment: str, get_list_func) -> bool:
        partner_num = self._process_digit_from_message(user_id, message, comment)

        if partner_num is False:
            return False

        people_list = get_list_func(user_id)

        if partner_num < 1 or partner_num > len(people_list):
            self._api.send_message(user_id, "Пользователя с таким номером нет в списке❗")
            return False

        partner = people_list[partner_num - 1]

        city_name = partner.city.name if partner.city else ""
        region_name = partner.region.name if partner.region else ""

        user_info = get_user_info_str(partner.partner_vk_id, partner.first_name, partner.last_name, partner.bdate,
                                      city_name, region_name)

        photo_attachments = [get_attachment_photo(photo.owner_id, photo.media_id)
                             for photo in partner.photos]

        self._api.send_message(user_id, user_info, attachments=photo_attachments)

        return True

    def _show_favorite_photos(self, user_id: int, message: str) -> bool:
        comment = "порядковый номер профиля из избранных"
        return self.__show_partner_photos(user_id, message, comment, self._db.get_favorites)

    def _show_blacklist_person_photos(self, user_id: int, message: str) -> bool:
        comment = "порядковый номер профиля из блэклиста"
        return self.__show_partner_photos(user_id, message, comment, self._db.get_blacklist)

    def _show_favorites(self, user_id: int) -> bool:
        favorites_info, res_get_partners_info = self._get_partners_info_from_favorites(user_id)
        if not res_get_partners_info:
            self._api.send_message(user_id, favorites_info)
            self._show_main_menu(user_id)
            return False

        self._api.send_message(user_id, favorites_info,
                               favorites_keyboard)

        return True

    def _show_blacklist(self, user_id: int) -> bool:
        blacklist_info, res_get_partners_info = self._get_partners_info_from_blacklist(user_id)
        if not res_get_partners_info:
            self._api.send_message(user_id, blacklist_info)
            self._show_main_menu(user_id)
            return False

        self._api.send_message(user_id, blacklist_info,
                               blacklist_keyboard)

        return True

    def _show_settings(self, user_id: int) -> bool:
        settings = self._db.get_user_settings(user_id)

        if not settings:
            self._api.send_message(user_id, "Не получилось найти текущие настройки. "
                                            "Попробуйте повторить операцию ещё раз❗")
            return False

        sex_index = settings.sex_index
        age_from = settings.age_from
        age_to = settings.age_to
        city_name = ''
        region_name = ''
        if settings.city:
            city_name = settings.city.name
            if settings.region:
                region_name = settings.region.name

        sex_name = get_sex_str(sex_index)
        age_info = get_age_range_str(age_from, age_to)
        location_info = get_location_str(city_name, region_name)

        info_text = (f"Настройки для поиска 🔍\n"
                     f"Город: {location_info}\n"
                     f"Пол: {sex_name}\n"
                     f"Возраст: {age_info}")

        self._api.send_message(user_id, info_text, settings_menu_keyboard)

        return True

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

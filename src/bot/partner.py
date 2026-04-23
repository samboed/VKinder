import random

from src.bot.base import BotBase
from src.bot.constants import QTY_SEND_PROFILE_PHOTOS, QTY_SEND_MARK_PHOTOS
from src.bot.formatters import get_user_info_str
from src.bot.keyboard import (button_user_to_blacklist, button_user_to_favorites,
                              button_main_menu, payload_candidate_data_keyword)
from src.bot.message_processing import BotMessage
from src.bot.message_texts import (SHOW_PHOTOS_FAVORITES_PERSON_TEXT, SHOW_PHOTOS_BLACKLIST_PERSON_TEXT,
                                   DEL_PHOTOS_FAVORITES_PERSON_TEXT, DEL_PHOTOS_BLACKLIST_PERSON_TEXT)
from src.bot.types import Location
from src.vk_api.keyboard import Keyboard
from src.vk_api.types import User, Attachment


class BotPartner(BotMessage, BotBase):
    def __init__(self, group_token, user_token, group_id, engine):
        super().__init__(group_token, user_token, group_id, engine)

    def _get_partners_info_from_favorites(self, user_id: int) -> tuple[str, bool]:
        favorites = self._db.get_favorites(user_id)

        info_text = ''
        for person_num, partner in enumerate(favorites, start=1):
            city_name = partner.city.name if partner.city else ""
            region_name = partner.region.name if partner.region else ""

            partner_info = (f"{f'{person_num}.':5} " +
                           get_user_info_str(partner.partner_vk_id, partner.first_name,
                                             partner.last_name, partner.bdate, city_name,
                                             region_name, False) + "\n")

            info_text += partner_info

        if not info_text:
            return "Список избранных пуст 🪹", False

        info_text = "Список избранных ❤️‍🔥:\n" + info_text

        return info_text, True

    def _get_partners_info_from_blacklist(self, user_id: int) -> tuple[str, bool]:
        blacklist = self._db.get_blacklist(user_id)

        info_text = ''
        for person_num, partner in enumerate(blacklist, start=1):
            city_name = partner.city.name if partner.city else ""
            region_name = partner.region.name if partner.region else ""

            partner_info = (f"{f'{person_num}.':5} " +
                           get_user_info_str(partner.partner_vk_id, partner.first_name,
                                             partner.last_name, partner.bdate, city_name,
                                             region_name, False) + "\n")

            info_text += partner_info

        if not info_text:
            return "Стоп-лист пуст 🪹", False

        info_text = "Стоп-лист 💔:\n" + info_text

        return info_text, True

    def _ask_profile_number_for_show_photos_from_favorites(self, user_id: int):
        self._api.send_message(user_id, SHOW_PHOTOS_FAVORITES_PERSON_TEXT)

    def _ask_profile_number_for_show_photos_from_blacklist(self, user_id: int):
        self._api.send_message(user_id, SHOW_PHOTOS_BLACKLIST_PERSON_TEXT)

    def _ask_profile_number_for_del_from_favorites(self, user_id: int):
        self._api.send_message(user_id, DEL_PHOTOS_FAVORITES_PERSON_TEXT)

    def _ask_profile_number_for_del_from_blacklist(self, user_id: int):
        self._api.send_message(user_id, DEL_PHOTOS_BLACKLIST_PERSON_TEXT)

    def __process_del_person(self, user_id: int, result_delete_person: bool,
                             first_name: str, last_name: str, postfix_comment: str):
        if not result_delete_person:
            delete_fail_message = (f"Не удалось удалить пользователя "
                                   f"{first_name} {last_name} {postfix_comment}")
            self._api.send_message(user_id, delete_fail_message)
            return False

        delete_done_message = (f"Был удалён пользователь "
                               f"{first_name} {last_name} {postfix_comment}")
        self._api.send_message(user_id, delete_done_message)

        return True

    def __del_partner_from_table(self, user_id: int, message: str,
                                 get_partners_func, del_person_from_db_func,
                                 comment: str, postfix_comment: str):
        partner_num = self._process_digit_from_message(user_id, message, comment)

        if partner_num is False:
            return False

        partners = get_partners_func(user_id)

        if partner_num < 1 or partner_num > len(partners):
            self._api.send_message(user_id, f"Указан неверный {comment}. "
                                            f"Пользователя с номером {partner_num} нет в списке. "
                                            f"Попробуйте ещё раз❗")
            return False

        partner = partners[partner_num - 1]
        first_name = partner.first_name
        last_name = partner.last_name

        result_delete_person = del_person_from_db_func(user_id, partner.partner_vk_id)

        return self.__process_del_person(user_id, result_delete_person,
                                         first_name, last_name, postfix_comment)

    def _del_favorite(self, user_id: int, message: str):
        comment = "порядковый номер профиля из избранных"
        return self.__del_partner_from_table(user_id, message,
                                             self._db.get_favorites,
                                             self._db.delete_favorite_partner,
                                             comment, "из избранных ❤️‍🔥")

    def _del_blacklist_person(self, user_id: int, message: str):
        comment = "порядковый номер профиля из блэклиста"
        return self.__del_partner_from_table(user_id, message,
                                             self._db.get_blacklist,
                                             self._db.delete_blacklist_partner,
                                             comment, "из блэклиста 💔")

    def _save_candidate(self, user_id: int, payload: dict, add_candidate_to_db_func):
        partner, partner_photos = self.__unpack_candidate_payload(payload)

        settings = self._db.get_user_settings(user_id)
        self._db.add_partner(partner.id, partner.first_name, partner.last_name,
                             partner.bdate, settings.city_id,
                             settings.region_id)

        for owner_id, media_id in partner_photos:
            self._db.add_photo(partner.id, owner_id, media_id)

        add_candidate_to_db_func(user_id, partner.id)

    @staticmethod
    def __pack_candidate_payload(candidate_data: User, candidate_photos: list[Attachment]):
        candidate_id = candidate_data.id
        candidate_first_name = candidate_data.first_name
        candidate_last_name = candidate_data.last_name
        candidate_bdate = candidate_data.bdate

        candidate_photos_data = []
        for candidate_photo in candidate_photos:
            candidate_photos_data.append((candidate_photo.owner_id, candidate_photo.media_id))

        return [candidate_id, candidate_first_name, candidate_last_name, candidate_bdate, candidate_photos_data]

    @staticmethod
    def __unpack_candidate_payload(payload):
        (candidate_id, candidate_first_name, candidate_last_name,
         candidate_bdate, candidate_photos_data) = payload[payload_candidate_data_keyword]

        user = User(candidate_id, candidate_first_name, candidate_last_name, '', candidate_bdate, '', '')

        return user, candidate_photos_data

    def _start_search(self, user_id: int):
        res_search_new_panther = self.__search_new_panther(user_id)
        if not res_search_new_panther:
            self._api.send_message(user_id, "Не удалось найти пару, попробуйте ещё раз! ❤️‍🩹")
            return False

        candidate_data, candidate_location, candidate_photos = res_search_new_panther

        candidate_info = get_user_info_str(candidate_data.id,
                                           candidate_data.first_name,
                                           candidate_data.last_name,
                                           candidate_data.bdate,
                                           candidate_location.city_name,
                                           candidate_location.region_name)

        payload_data = self.__pack_candidate_payload(candidate_data, candidate_photos)

        button_user_to_blacklist.update_payload(payload_candidate_data_keyword, payload_data)
        button_user_to_favorites.update_payload(payload_candidate_data_keyword, payload_data)

        search_keyboard = Keyboard([[button_user_to_blacklist, button_user_to_favorites],
                                    [button_main_menu]])

        self._api.send_message(user_id, candidate_info,
                               search_keyboard,
                               candidate_photos)

        return True

    def __search_new_panther(self, user_id: int):
        settings = self._db.get_user_settings(user_id)

        region_id = settings.region_id
        region_name = ''
        if region_id:
            region_name = settings.region.name
        city_id = settings.city_id
        city_name = settings.city.name
        sex_ind = settings.sex_index
        age_from = settings.age_from
        age_to = settings.age_to

        excluded_ids = self._db.get_excluded_partner_ids(user_id)

        user_data = None
        offset_search = 0
        while not user_data:
            res_get_users = self._api.search_user(city_id, sex_ind, age_from, age_to, offset_search)
            if not res_get_users:
                return False

            users = res_get_users

            filtered_users = [user for user in users if user.id not in excluded_ids]

            if len(filtered_users):
                user_data = filtered_users[random.randint(0, len(filtered_users) - 1)]

            offset_search = len(users)

        user_profile_photos = []
        user_mark_photos = []

        res_get_user_profile_photos = self._api.get_photos(user_data.id, "profile")
        if res_get_user_profile_photos:
            user_profile_photos = res_get_user_profile_photos
            user_profile_photos.sort(key=lambda photo: photo.like_count, reverse=True)
            user_profile_photos = user_profile_photos[:QTY_SEND_PROFILE_PHOTOS]

        res_get_user_mark_photos = self._api.get_user_mark_photos(user_data.id)
        if res_get_user_mark_photos:
            user_mark_photos = res_get_user_mark_photos
            user_mark_photos.sort(key=lambda photo: photo.like_count, reverse=True)
            user_mark_photos = user_mark_photos[:QTY_SEND_MARK_PHOTOS]

        photos_list = user_profile_photos + user_mark_photos

        attachments = [photo.attachment for photo in photos_list]
        user_location = Location(city_id, city_name, region_id, region_name)

        return user_data, user_location, attachments

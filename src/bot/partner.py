from src.bot.base import BotBase
from src.bot.constants import QTY_SEND_PROFILE_PHOTOS, QTY_SEND_MARK_PHOTOS
from src.bot.formatters import get_profile_link, get_user_info_str, get_location_str
from src.bot.keyboard import button_user_to_blacklist, payload_user_id_keyword, button_user_to_favorites, \
    button_main_menu
from src.bot.message_processing import BotMessage
from src.bot.message_texts import SHOW_PHOTOS_FAVORITES_PERSON_TEXT, SHOW_PHOTOS_BLACKLIST_PERSON_TEXT, \
    DEL_PHOTOS_FAVORITES_PERSON_TEXT, DEL_PHOTOS_BLACKLIST_PERSON_TEXT
from src.bot.types import Location
from src.vk_api.keyboard import Keyboard


class BotPartner(BotMessage, BotBase):
    def __init__(self, group_token, user_token, group_id):
        super().__init__(group_token, user_token, group_id)

    def _get_general_people_info_from_favorites(self, user_id: int) -> str:
        favorites = self.db.get_favorites(user_id)

        info_text = ''
        for person_num, candidate in enumerate(favorites, start=1):
            profile_link = get_profile_link(candidate.vk_id)
            city_name = candidate.city.name if candidate.city else ""
            region_name = candidate.region.name if candidate.region else ""
            location = get_location_str(city_name, region_name)

            info_text += (
                f"{f'{person_num}.':5} {candidate.first_name.capitalize()} {candidate.last_name.capitalize()}, "
                f"{location} {profile_link}\n")

        if info_text:
            info_text = "Список избранных ❤️‍🔥:\n" + info_text
        else:
            info_text = "Список избранных пуст 🪹"

        return info_text

    def _get_general_people_info_from_blacklist(self, user_id: int) -> str:
        blacklist = self.db.get_blacklist(user_id)

        info_text = ''
        for person_num, candidate in enumerate(blacklist, start=1):
            profile_link = get_profile_link(candidate.vk_id)
            city_name = candidate.city.name if candidate.city else ""
            region_name = candidate.region.name if candidate.region else ""
            location = get_location_str(city_name, region_name)

            info_text += (
                f"{f'{person_num}.':5} {candidate.first_name.capitalize()} {candidate.last_name.capitalize()}, "
                f"{location} {profile_link}\n")

        if info_text:
            info_text = "Стоп-лист 💔:\n" + info_text
        else:
            info_text = "Стоп-лист пуст 🪹"

        return info_text

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
        if result_delete_person:
            delete_done_message = (f"Был удалён пользователь "
                                   f"{first_name} {last_name} {postfix_comment}")
            self._api.send_message(user_id, delete_done_message)
        else:
            delete_fail_message = (f"Не удалось удалить пользователя "
                                   f"{first_name} {last_name} {postfix_comment}")
            self._api.send_message(user_id, delete_fail_message)
            return False

        return True

    def __del_person_from_table(self, user_id: int, message: str,
                                get_list_func, del_person_from_db_func,
                                comment: str, postfix_comment: str):
        person_num = self._process_digit_from_message(user_id, message, comment)

        if not person_num:
            return False

        people_list = get_list_func(user_id)

        if person_num < 1 or person_num > len(people_list):
            self._api.send_message(user_id, "Пользователя с таким номером нет в списке.")
            return False

        candidate = people_list[person_num - 1]
        first_name = candidate.first_name
        last_name = candidate.last_name

        result_delete_person = del_person_from_db_func(user_id, candidate.vk_id)

        return self.__process_del_person(user_id, result_delete_person,
                                         first_name, last_name, postfix_comment)

    def _del_favorite(self, user_id: int, message: str):
        comment = "порядковый номер профиля из избранных"
        return self.__del_person_from_table(user_id, message,
                                            self.db.get_favorites,
                                            self.db.delete_favorite,
                                            comment, "из избранных ❤️‍🔥")

    def _del_blacklist_person(self, user_id: int, message: str):
        comment = "порядковый номер профиля из блэклиста"
        return self.__del_person_from_table(user_id, message,
                                            self.db.get_blacklist,
                                            self.db.delete_blacklist,
                                            comment, "из блэклиста 💔")

    def _start_search(self, user_id: int):
        panther_data, panther_location, panther_photos = self.__search_new_panther(user_id)

        panther_info = get_user_info_str(panther_data.id,
                                         panther_data.first_name,
                                         panther_data.last_name,
                                         panther_location.city_name,
                                         panther_location.region_name)

        button_user_to_blacklist.update_payload(payload_user_id_keyword, panther_data.id)
        button_user_to_favorites.update_payload(payload_user_id_keyword, panther_data.id)

        search_keyboard = Keyboard([[button_user_to_blacklist, button_user_to_favorites],
                                    [button_main_menu]])

        self._api.send_message(user_id, panther_info,
                               search_keyboard,
                               panther_photos)

    def __search_new_panther(self, user_id: int):
        settings = self.db.get_user_settings(user_id)

        region_id = settings.region_id
        region_name = settings.region_name
        city_id = settings.city_id
        city_name = settings.city_name
        sex_ind = settings.sex_index
        age_from = settings.age_from
        age_to = settings.age_to

        excluded_ids = self.db.get_excluded_partner_ids(user_id)

        user_data = self._api.search_user(city_id, sex_ind, age_from, age_to, excluded_ids)

        user_profile_photos = self._api.get_photos(user_data.id, "profile")
        user_profile_photos.sort(key=lambda photo: photo.like_count, reverse=True)
        user_profile_photos = user_profile_photos[:QTY_SEND_PROFILE_PHOTOS]

        user_mark_photos = self._api.get_user_mark_photos(user_data.id)
        if user_mark_photos:
            user_mark_photos.sort(key=lambda photo: photo.like_count, reverse=True)
            user_mark_photos = user_mark_photos[:QTY_SEND_MARK_PHOTOS]
        else:
            user_mark_photos = []

        photos_list = user_profile_photos + user_mark_photos
        attachments = [photo.attachment for photo in photos_list]

        user_location = Location(city_id, city_name, region_id, region_name)

        return user_data, user_location, attachments

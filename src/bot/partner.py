from src.bot.base import BotBase
from src.bot.message_processing import BotMessage
from src.bot.constants import QTY_SEND_PROFILE_PHOTOS, QTY_SEND_MARK_PHOTOS
from src.bot.formatters import get_profile_link, get_location_str, get_user_info_str
from src.bot.keyboard import button_user_to_blacklist, payload_user_id_keyword, button_user_to_favorites, \
    button_main_menu
from src.bot.message_texts import SHOW_PHOTOS_FAVORITES_PERSON_TEXT, SHOW_PHOTOS_BLACKLIST_PERSON_TEXT, \
    DEL_PHOTOS_FAVORITES_PERSON_TEXT, DEL_PHOTOS_BLACKLIST_PERSON_TEXT
from src.bot.types import Location
from src.vk_api.keyboard import Keyboard


import src.bot.testing as testing # TODO: for testing
dialog_states = testing.dialog_states #TODO: delete it and get state from db
is_new_user = testing.is_new_user  # TODO: for testing
region_name = testing.region_name # TODO: for testing
reg_id = testing.reg_id # TODO: for testing
city_id = testing.city_id # TODO: for testing
city_name = testing.city_name # TODO: for testing
sex_ind = testing.sex_ind # TODO: for testing
age_from = testing.age_from # TODO: for testing
age_to = testing.age_to # TODO: for testing


class BotPartner(BotMessage, BotBase):
    def __init__(self, group_token, user_token, group_id):
        super().__init__(group_token, user_token, group_id)

    @staticmethod
    def _get_general_people_info_from_favorites(user_id: int) -> str:
        # TODO: get general people info list from Favorites table
        # people_list = get_from_db_func(user_id) # TODO: insert your realization
        # user_id, first_name, last_name, city_name, region_name
        people_list = [(1, "Маша", "Романова", "Самара", "Самарская область")]  # test example
        ###

        info_text = ''
        for person_num, (favorite_id, first_name, last_name, city_name, region_name) in enumerate(people_list, start=1):
            profile_link = get_profile_link(favorite_id)
            location = get_location_str(city_name, region_name)

            info_text += (f"{f'{person_num}.':5} {first_name.capitalize()} {last_name.capitalize()}, "
                          f"{location} {profile_link}\n")

        if info_text:
            info_text = "Список избранных ❤️‍🔥:\n" + info_text
        else:
            info_text = "Список избранных пуст 🪹"

        return info_text

    @staticmethod
    def _get_general_people_info_from_blacklist(user_id: int) -> str:
        # TODO: get general people info list from Blacklist table
        # people_list = get_from_db_func(user_id) # TODO: insert your realization
        people_list = [(1, "Маша", "Романова", "Самара", "Самарская область")]  # TODO: for testing
        ###

        info_text = ''
        for person_num, (blacklist_person_id, first_name, last_name, city_name, region_name) in enumerate(people_list, start=1):
            profile_link = get_profile_link(blacklist_person_id)
            location = get_location_str(city_name, region_name)

            info_text += (f"{f'{person_num}.':5} {first_name.capitalize()} {last_name.capitalize()}, "
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
                             first_name: str, last_name: str,
                             location: str, postfix_comment: str):
        if result_delete_person:
            delete_done_message = (f"Был удалён пользователь "
                                   f"{first_name} {last_name}, {location} {postfix_comment}")
            self._api.send_message(user_id, delete_done_message)
        else:
            delete_fail_message = (f"Не удалось удалить пользователя "
                                   f"{first_name} {last_name}, {location} {postfix_comment}")
            self._api.send_message(user_id, delete_fail_message)
            return False

        return True

    def __del_person_from_table(self, user_id: int, message:str,
                                get_person_from_db_func, del_person_from_db_func,
                                comment: str, postfix_comment: str):
        person_num = self._process_digit_from_message(user_id, message, comment)

        if not person_num:
            return False

        # TODO: get info about blacklist person from Table (Favorites or Blacklist)
        # user_id, first_name, last_name, city_name, region_name = get_person_from_db_func(person_num)
        first_name = "First Name"  # TODO: for testing
        last_name = "Last Name"  # TODO: for testing
        city_name = "Test City"  # TODO: for testing
        region_name = "Test Region"  # TODO: for testing

        location = get_location_str(city_name, region_name)

        # TODO: del user from Blacklist
        # result_delete_person = del_person_from_db_func(user_id)
        result_delete_person = True

        return self.__process_del_person(user_id, result_delete_person,
                                         first_name, last_name, location,
                                         postfix_comment)

    def _del_favorite(self, user_id: int, message: str):
        comment = "порядковый номер профиля из избранных"

        get_person_from_db_func = lambda x: x  # TODO: for testing
        del_person_from_db_func = lambda x: x  # TODO: for testing

        return self.__del_person_from_table(user_id, message,
                                            get_person_from_db_func, del_person_from_db_func,
                                            comment, "из избранных ❤️‍🔥")

    def _del_blacklist_person(self, user_id: int, message: str):
        comment = "порядковый номер профиля из блэклиста"

        get_person_from_db_func = lambda x: x # TODO: for testing
        del_person_from_db_func = lambda x: x # TODO: for testing

        return self.__del_person_from_table(user_id, message,
                                            get_person_from_db_func, del_person_from_db_func,
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
        # TODO: get preference user from Preferences table
        # city_id, region_id, sex_index, age_from, age_to = get_from_db_func(user_id) # TODO: insert your realization
        # city_name = get_from_db_func(city_id) # TODO: add
        # region_name = get_from_db_func(region_id) # TODO: add
        region_id = testing.reg_id  # TODO: for testing
        region_name = testing.region_name # TODO: for testing
        city_id = testing.city_id  # TODO: for testing
        city_name = testing.city_name  # TODO: for testing
        sex_ind = testing.sex_ind # TODO: for testing
        age_from = testing.age_from # TODO: for testing
        age_to = testing.age_to # TODO: for testing
        ###

        user_data = self._api.search_user(city_id, sex_ind, age_from, age_to)

        # TODO: save candidate to DB (user_data.id, user_data.first_name, user_data.last_name, city_id, region_id)

        user_profile_photos = self._api.get_photos(user_data.id, "profile")

        user_profile_photos.sort(key=lambda photo: photo.like_count, reverse=True)
        user_profile_photos = user_profile_photos[:QTY_SEND_PROFILE_PHOTOS]
        user_profile_photos = [photo.attachment for photo in user_profile_photos]

        user_mark_photos = self._api.get_user_mark_photos(user_data.id)

        user_mark_photos.sort(key=lambda photo: photo.like_count, reverse=True)
        user_mark_photos = user_mark_photos[:QTY_SEND_MARK_PHOTOS]
        user_mark_photos = [photo.attachment for photo in user_mark_photos]

        photos_list = user_profile_photos + user_mark_photos

        for photo in photos_list:
            photo.media_id  # TODO: save media_id to Photos by user_data.id

        user_location = Location(city_id, city_name, region_id, region_name)

        return user_data, user_location, photos_list

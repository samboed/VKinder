from enum import IntEnum
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import namedtuple

from src.vk_api.api import API, Events, Sex
from src.vk_api.keyboard import Keyboard
from src.bot.keyboard import (button_main_menu, button_delete_user_from_blacklist,
                              button_user_to_blacklist, button_user_to_favorites,
                              button_show_user_from_blacklist, button_men_sex_preference_select,
                              button_women_sex_preference_select, button_all_sex_preference_select,
                              payload_command_keyword, payload_user_id_keyword, payload_value_keyword,
                              command_go_to_main_menu, command_search_panther, command_show_settings,
                              command_add_sex_prefer, command_show_favorites, command_show_blacklist,
                              command_add_user_to_blacklist, command_add_user_to_favorites,
                              command_show_user_from_blacklist, command_del_user_from_blacklist,
                              command_show_profile_photos_favorites, command_del_user_from_favorites,
                              command_setup_city, command_setup_sex, command_setup_age,
                              main_menu_keyboard, settings_menu_keyboard, button_show_user_from_favorites,
                              button_delete_user_from_favorites)


dialog_states = {} #TODO: delete it and get state from db
is_new_user = True  # TODO: for testing
region_name = '' # TODO: for testing
reg_id = None # TODO: for testing
city_id = None # TODO: for testing
city_name = '' # TODO: for testing
sex_ind = None # TODO: for testing
age_from = None # TODO: for testing
age_to = None # TODO: for testing

QTY_SEND_PROFILE_PHOTOS = 3
QTY_SEND_MARK_PHOTOS = 3

AGE_DEF_MIN_SEARCHING = 18
AGE_DEF_MAX_SEARCHING = 55

AGE_MIN_SEARCHING = 18
AGE_MAX_SEARCHING = 115

MAIN_MENU_TEXT = "Вы перешли в главное меню 🏠"
SPECIFY_REGION_TEXT = "Укажите регион для поиска 🌍"
SPECIFY_CITY_TEXT = "Укажите город для поиска 🏙️"
SELECT_SEX_TEXT = "Выберите пол партнёра для поиска ⚤"
SPECIFY_AGE_FROM_TEXT = "Укажите минимальный возраст для поиска 🔞"
SPECIFY_AGE_TO_TEXT = "Укажите максимальный возраст для поиска 💯"
SHOW_PHOTOS_FAVORITES_PERSON_TEXT = ("Напишите порядковый номер профиля из избранных ❤️‍🔥, "
                                     "для которого вы хотите увидеть фотографии 🖼️")
SHOW_PHOTOS_BLACKLIST_PERSON_TEXT = ("Напишите порядковый номер профиля из блэклиста 💔, "
                                     "для которого вы хотите увидеть фотографии 🖼️")
DEL_PHOTOS_FAVORITES_PERSON_TEXT = ("Напишите порядковый номер профиля из избранных ❤️‍🔥, "
                                    "который вы хотите удалить 🗑️")
DEL_PHOTOS_BLACKLIST_PERSON_TEXT = ("Напишите порядковый номер профиля из блэклиста 💔, "
                                    "который вы хотите удалить 🗑️")


def get_sex_str(sex_index: int):
    if sex_index == Sex.men.value:
        return "мужчины ♂️"
    elif sex_index == Sex.women.value:
        return "девушки ♀️"
    else:
        return "мужчины/девушки ⚤"


def get_age_range_str(age_from: int, age_to: int):
    if age_from == age_to:
        return str(age_from)
    return f"{age_from}-{age_to}"


def get_location_str(city_name: str, region_name: str = ''):
    if region_name:
        location_info_list = [city_name, region_name]
    else:
        location_info_list = [city_name]

    return ", ".join(location_info_list)


def get_user_info_str(user_id: int, first_name: str, last_name: str,
                      city_name: str = '', region_name: str = ''):
    profile_link = f"https://vk.com/id{user_id}"

    location_str = get_location_str(city_name, region_name)

    info_text = (f"{first_name} {last_name}, {location_str}\n"
                 f"{profile_link}")

    return info_text


Location = namedtuple("Location",
                      ["city_id", "city_name", "region_id", "region_name"],
                      defaults='')


class DialogStates(IntEnum):
    INITIAL = 0
    SETUP_REGION = 1
    SETUP_CITY = 2
    SETUP_AGE_FROM = 3
    SETUP_AGE_TO = 4
    SHOW_FAVORITE_PHOTO = 5
    SHOW_BLACKLIST_PERSON_PHOTO = 6
    DEL_FAVORITE = 7
    DEL_BLACKLIST_PERSON = 8


class Bot:
    def __init__(self, group_token, user_token, group_id):
        self.__api = API(group_token, user_token, group_id)

    def start(self):
        self.__handler_events()

    def __handler_events(self):
        for event, user_id, payload in self.__api.polling_events():
            if event == Events.SEND_MESSAGE:
                message = payload

                # TODO: get dialog user state from Table
                dialog_user_state = dialog_states[user_id]

                if dialog_user_state == DialogStates.SETUP_REGION:
                    res_setup_region = self.__setup_region(user_id, message)
                    if res_setup_region:
                        dialog_states[user_id] = DialogStates.SETUP_CITY # TODO: update DialogState
                        self.__show_city_setup(user_id)
                elif dialog_user_state == DialogStates.SETUP_CITY:
                    res_setup_city = self.__setup_city(user_id, message)
                    if res_setup_city:
                        dialog_states[user_id] = DialogStates.INITIAL # TODO: update DialogState
                        self.__show_settings(user_id)
                elif dialog_user_state == DialogStates.SETUP_AGE_FROM:
                    res_setup_age_from = self.__setup_age_from(user_id, message)
                    if res_setup_age_from:
                        dialog_states[user_id] = DialogStates.SETUP_AGE_TO # TODO: update DialogState
                        self.__show_age_to_setting(user_id)
                elif dialog_user_state == DialogStates.SETUP_AGE_TO:
                    res_setup_age_to = self.__setup_age_to(user_id, message)
                    if res_setup_age_to:
                        dialog_states[user_id] = DialogStates.INITIAL # TODO: update DialogState
                        self.__show_settings(user_id)
                elif dialog_user_state == DialogStates.SHOW_FAVORITE_PHOTO:
                    res_show_favorite_photos = self.__show_favorite_photos(user_id, message)
                    if res_show_favorite_photos:
                        dialog_states[user_id] = DialogStates.INITIAL # TODO: update DialogState
                elif dialog_user_state == DialogStates.SHOW_BLACKLIST_PERSON_PHOTO:
                    res_show_blacklist_photos = self.__show_blacklist_person_photos(user_id, message)
                    if res_show_blacklist_photos:
                        dialog_states[user_id] = DialogStates.INITIAL # TODO: update DialogState
                elif dialog_user_state == DialogStates.DEL_FAVORITE:
                    res_del_favorite = self.__del_favorite(user_id, message)
                    if res_del_favorite:
                        dialog_states[user_id] = DialogStates.INITIAL # TODO: update DialogState
                        self.__show_favorites(user_id)
                elif dialog_user_state == DialogStates.DEL_BLACKLIST_PERSON:
                    res_del_blacklist_person = self.__del_blacklist_person(user_id, message)
                    if res_del_blacklist_person:
                        dialog_states[user_id] = DialogStates.INITIAL # TODO: update DialogState
                        self.__show_blacklist(user_id)

            elif event == Events.PUSH_BUTTON:
                if payload[payload_command_keyword] == "start":
                    # TODO: check user in Users table
                    global is_new_user # TODO: for testing

                    if is_new_user:
                        self.__setup_and_show_init_settings(user_id)
                        dialog_states[user_id] = DialogStates.INITIAL # TODO: update DialogState
                        self.__show_main_menu(user_id)
                elif payload[payload_command_keyword] == command_search_panther:
                    self.__start_search(user_id)
                elif payload[payload_command_keyword] == command_show_settings:
                    self.__show_settings(user_id)
                elif payload[payload_command_keyword] == command_show_favorites:
                    self.__show_favorites(user_id)
                elif payload[payload_command_keyword] == command_show_blacklist:
                    self.__show_blacklist(user_id)
                elif payload[payload_command_keyword] == command_show_profile_photos_favorites:
                    dialog_states[user_id] = DialogStates.SHOW_FAVORITE_PHOTO # TODO: update DialogState
                    self.__ask_profile_number_for_show_photos_from_favorites(user_id)
                elif payload[payload_command_keyword] == command_show_user_from_blacklist:
                    dialog_states[user_id] = DialogStates.SHOW_BLACKLIST_PERSON_PHOTO # TODO: update DialogState
                    self.__ask_profile_number_for_show_photos_from_blacklist(user_id)
                elif payload[payload_command_keyword] == command_del_user_from_favorites:
                    dialog_states[user_id] = DialogStates.DEL_FAVORITE # TODO: update DialogState
                    self.__ask_profile_number_for_del_from_favorites(user_id)
                elif payload[payload_command_keyword] == command_del_user_from_blacklist:
                    dialog_states[user_id] = DialogStates.DEL_BLACKLIST_PERSON # TODO: update DialogState
                    self.__ask_profile_number_for_del_from_blacklist(user_id)
                elif payload[payload_command_keyword] == command_add_user_to_favorites:
                    panther_user_id = payload[payload_user_id_keyword]

                    # TODO: add panther_user_id to Favorites table

                    self.__start_search(user_id)
                elif payload[payload_command_keyword] == command_add_user_to_blacklist:
                    panther_user_id = payload[payload_user_id_keyword]

                    # TODO: add panther_user_id to Blacklist table

                    self.__start_search(user_id)
                elif payload[payload_command_keyword] == command_add_sex_prefer:
                    sex = payload[payload_value_keyword]
                    self.__setup_sex(user_id, sex)
                    self.__show_settings(user_id)
                elif payload[payload_command_keyword] == command_setup_city:
                    dialog_states[user_id] = DialogStates.SETUP_REGION
                    self.__show_region_setup(user_id)
                elif payload[payload_command_keyword] == command_setup_sex:
                    self.__show_sex_setup(user_id)
                elif payload[payload_command_keyword] == command_setup_age:
                    dialog_states[user_id] = DialogStates.SETUP_AGE_FROM
                    self.__show_age_from_setting(user_id)
                elif payload[payload_command_keyword] == command_go_to_main_menu:
                    dialog_states[user_id] = DialogStates.INITIAL
                    self.__show_main_menu(user_id)

    def __get_age_from_message(self, user_id: int, message: str, comment: str):
        filtered_message = message.strip()
        if filtered_message.isdigit():
            age = int(filtered_message)
            if age < AGE_MIN_SEARCHING:
                warn_message = (f"Указан неверный {comment}. Возраст должен быть больше {AGE_MIN_SEARCHING} лет. "
                                f"Попробуйте ещё раз❗")
                self.__api.send_message(user_id, warn_message)
                return False
            elif age > AGE_MAX_SEARCHING:
                warn_message = (f"Указан неверный {comment}. Возраст должен быть меньше {AGE_MAX_SEARCHING} лет. "
                                f"Попробуйте ещё раз❗")
                self.__api.send_message(user_id, warn_message)
                return False
        else:
            self.__api.send_message(user_id, f"Указан неверный {comment}. Возраст должен быть указан числом. "
                                             f"Попробуйте ещё раз❗")
            return False

        return age

    def __get_digit_from_message(self, user_id: int, message: str, comment: str):
        filtered_message = message.strip()
        if not filtered_message.isdigit():
            self.__api.send_message(user_id, f"Указан неверный {comment}. "
                                             f"Порядковый номер должен быть указан числом. "
                                             f"Попробуйте ещё раз❗")
            return False
        return filtered_message

    @staticmethod
    def __get_general_people_info_from_favorites(user_id: int) -> str:
        # TODO: get general people info list from Favorites table
        # annotation: list[tuple(str, str, str)], example: (Пётр, Тютчев, link-to-vk-profile)
        # people_list = get_from_db_func(user_id) # TODO: insert your realization
        people_list = [("Маша", "Романова", "Самара", "https://vk.com/id102774978")]  # test example
        ###
        info_text = ''
        for person_num, (first_name, last_name, city, profile_link) in enumerate(people_list, start=1):
            info_text += (f"{f'{person_num}.':5} {first_name.capitalize()} {last_name.capitalize()}, "
                          f"г. {city} {profile_link}\n")

        if info_text:
            info_text = "Список избранных ❤️‍🔥:\n" + info_text
        else:
            info_text = "Список избранных пуст 🪹"

        return info_text

    @staticmethod
    def __get_general_people_info_from_blacklist(user_id: int) -> str:
        # TODO: get general people info list from Blacklist table
        # annotation: list[tuple(str, str, str)], example: [(Лидия, Макарова, city, link-to-vk-profile)]
        # people_list = get_from_db_func(user_id) # TODO: insert your realization
        people_list = [("Лидия", "Макарова", "Волгоград", "https://vk.com/id548929585"),
                       ("Пётр", "Тютчев", "Москва", "https://vk.com/id731749219")]  # test example
        ###
        info_text = ''
        for person_num, (first_name, last_name, city, profile_link) in enumerate(people_list, start=1):
            info_text += (f"{f'{person_num}.':5} {first_name.capitalize()} {last_name.capitalize()}, "
                          f"г. {city.capitalize()} {profile_link}\n")

        if info_text:
            info_text = "Стоп-лист 💔:\n" + info_text
        else:
            info_text = "Стоп-лист пуст 🪹"

        return info_text

    def __show_main_menu(self, user_id: int):
        self.__api.send_message(user_id, MAIN_MENU_TEXT, main_menu_keyboard)

    def __show_favorite_photos(self, user_id: int, message: str):
        comment = "порядковый номер профиля из избранных"

        favorite_num = self.__get_digit_from_message(user_id, message, comment)

        if not favorite_num:
            return False

        # TODO: get first_name, last_name, city_name, region_name, user_id, media_id_list from Favorites
        # favorite_id, favorite_first_name, favorite_last_name, city_name, region_name = get_from_db(favorite_num)
        favorite_id = 1 # TODO: for testing
        favorite_first_name = "First Name" # TODO: for testing
        favorite_last_name = "Last Name" # TODO: for testing
        city_name = "Test City" # TODO: for testing
        region_name = "Test Region" # TODO: for testing
        media_id_list = [] # TODO: for testing, get from db by favorite_id

        panther_info = get_user_info_str(favorite_id,
                                         favorite_first_name,
                                         favorite_last_name,
                                         city_name,
                                         region_name)

        photo_attachments = []
        for media_id in media_id_list:
            photo_attachments.append(self.__api.get_attachment_photo(favorite_id, media_id))

        self.__api.send_message(user_id, panther_info, attachments=photo_attachments)

        return True

    def __show_blacklist_person_photos(self, user_id: int, message: str):
        comment = "порядковый номер профиля из блэклиста"

        favorite_num = self.__get_digit_from_message(user_id, message, comment)

        if not favorite_num:
            return False

        # TODO: get first_name, last_name, city_name, region_name, user_id, media_id_list from Blacklist
        # favorite_id, favorite_first_name, favorite_last_name, city_name, region_name = get_from_db(favorite_num)
        favorite_id = 1 # TODO: for testing
        favorite_first_name = "First Name" # TODO: for testing
        favorite_last_name = "Last Name" # TODO: for testing
        city_name = "Test City" # TODO: for testing
        region_name = "Test Region" # TODO: for testing
        media_id_list = [] # TODO: for testing, get from db by favorite_id

        panther_info = get_user_info_str(favorite_id,
                                         favorite_first_name,
                                         favorite_last_name,
                                         city_name,
                                         region_name)

        photo_attachments = []
        for media_id in media_id_list:
            photo_attachments.append(self.__api.get_attachment_photo(favorite_id, media_id))

        self.__api.send_message(user_id, panther_info, attachments=photo_attachments)

        return True

    def __show_favorites(self, user_id: int):
        favorites_keyboard = Keyboard([[button_show_user_from_favorites],
                                       [button_delete_user_from_favorites],
                                       [button_main_menu]])
        favorites_info = self.__get_general_people_info_from_favorites(user_id)
        self.__api.send_message(user_id, favorites_info,
                                favorites_keyboard)

    def __show_blacklist(self, user_id: int):
        blacklist_keyboard = Keyboard([[button_show_user_from_blacklist],
                                       [button_delete_user_from_blacklist],
                                       [button_main_menu]])
        blacklist_info = self.__get_general_people_info_from_blacklist(user_id)
        self.__api.send_message(user_id, blacklist_info,
                                blacklist_keyboard)

    def __show_settings(self, user_id: int):
        # TODO: get preference data from table UserPreferences
        # annotation: tuple(str, str, str), (сity_name, region_name, sex_index, ) example: (Москва, '',  Тютчев, link-to-vk-profile)
        # city_name, region_name, sex_index, age_from, age_to = get_from_db_func(user_id) # TODO: insert your realization
        ###
        sex_index = sex_ind # TODO: for testing

        sex_name = get_sex_str(sex_index)

        age_info = get_age_range_str(age_from, age_to)

        location_info = get_location_str(city_name, region_name)

        info_text = (f"Настройки для поиска 🔍\n"
                     f"Город: {location_info}\n"
                     f"Пол: {sex_name}\n"
                     f"Возраст: {age_info}")

        self.__api.send_message(user_id, info_text, settings_menu_keyboard)

        return info_text

    def __show_region_setup(self, user_id: int):
        self.__api.send_message(user_id, SPECIFY_REGION_TEXT)

    def __show_city_setup(self, user_id: int):
        self.__api.send_message(user_id, SPECIFY_CITY_TEXT)

    def __show_sex_setup(self, user_id: int):
        sex_setting_keyboard = Keyboard([[button_men_sex_preference_select,
                                          button_women_sex_preference_select,
                                          button_all_sex_preference_select]])
        self.__api.send_message(user_id, SELECT_SEX_TEXT, sex_setting_keyboard)

    def __show_age_from_setting(self, user_id: int):
        self.__api.send_message(user_id, SPECIFY_AGE_FROM_TEXT)

    def __show_age_to_setting(self, user_id: int):
        self.__api.send_message(user_id, SPECIFY_AGE_TO_TEXT)

    def __ask_profile_number_for_show_photos_from_favorites(self, user_id: int):
        self.__api.send_message(user_id, SHOW_PHOTOS_FAVORITES_PERSON_TEXT)

    def __ask_profile_number_for_show_photos_from_blacklist(self, user_id: int):
        self.__api.send_message(user_id, SHOW_PHOTOS_BLACKLIST_PERSON_TEXT)

    def __ask_profile_number_for_del_from_favorites(self, user_id: int):
        self.__api.send_message(user_id, DEL_PHOTOS_FAVORITES_PERSON_TEXT)

    def __ask_profile_number_for_del_from_blacklist(self, user_id: int):
        self.__api.send_message(user_id, DEL_PHOTOS_BLACKLIST_PERSON_TEXT)

    def __del_favorite(self, user_id: int, message: str):
        comment = "порядковый номер профиля из избранных"

        favorite_num = self.__get_digit_from_message(user_id, message, comment)

        if not favorite_num:
            return False

        # TODO: get info about blacklist person from Blacklist
        # user_id, first_name, last_name, city_name, region_name = get_from_db(favorite_num)
        first_name = "First Name"  # TODO: for testing
        last_name = "Last Name"  # TODO: for testing
        city_name = "Test City"  # TODO: for testing
        region_name = "Test Region"  # TODO: for testing

        location = get_location_str(city_name, region_name)

        # TODO: del user from Blacklist
        # result_delete_blacklist_person = delete_blacklist_person(user_id)
        result_delete_blacklist_person = True

        if result_delete_blacklist_person:
            delete_done_message = (f"Был удалён пользователь "
                                   f"{first_name} {last_name}, {location} из избранных ❤️‍🔥")
            self.__api.send_message(user_id, delete_done_message)
        else:
            delete_fail_message = (f"Не удалось удалить пользователя "
                                   f"{first_name} {last_name}, {location} из избранных ❤️‍🔥")
            self.__api.send_message(user_id, delete_fail_message)
            return False

        return True

    def __del_blacklist_person(self, user_id: int, message: str):
        comment = "порядковый номер профиля из блэклиста"

        favorite_num = self.__get_digit_from_message(user_id, message, comment)

        if not favorite_num:
            return False

        # TODO: get info about blacklist person from Blacklist
        # user_id, first_name, last_name, city_name, region_name = get_from_db(favorite_num)
        favorite_first_name = "First Name"  # TODO: for testing
        favorite_last_name = "Last Name"  # TODO: for testing
        city_name = "Test City"  # TODO: for testing
        region_name = "Test Region"  # TODO: for testing

        location = get_location_str(city_name, region_name)

        # TODO: del user from Blacklist
        # result_delete_blacklist_person = delete_blacklist_person(user_id)
        result_delete_blacklist_person = True

        if result_delete_blacklist_person:

            delete_done_message = (f"Был удалён пользователь "
                                   f"{favorite_first_name} {favorite_last_name}, {location} из блэклиста ⚫")
            self.__api.send_message(user_id, delete_done_message)
        else:
            delete_fail_message = (f"Не удалось удалить пользователя "
                                   f"{favorite_first_name} {favorite_last_name}, {location} из блэклиста ⚫")
            self.__api.send_message(user_id, delete_fail_message)
            return False

        return True

    def __setup_and_show_init_settings(self, user_id: int):
        user_data = self.__api.get_info_about_user(user_id)

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
            setup_age_from = 18
            setup_age_to = 55

        # TODO: save user in Users table
        global is_new_user # TODO: for testing
        is_new_user = False # TODO: for testing

        # TODO: save setup_city_id, setup_city_name, setup_sex, setup_age_from, setup_age_to in Preferences table
        global city_id, city_name, sex_ind, age_from, age_to
        city_id = setup_city_id # TODO: for testing
        city_name = setup_city_name # TODO: for testing
        sex_ind = setup_sex # TODO: for testing
        age_from = setup_age_from # TODO: for testing
        age_to = setup_age_to # TODO: for testing

        sex_name = get_sex_str(setup_sex)

        age_info = get_age_range_str(age_from, age_to)

        location_info = get_location_str(city_name)

        info_text = (f"Были установлены следующие настройки для поиска 🔍\n"
                     f"Город: {location_info}\n"
                     f"Пол: {sex_name}\n"
                     f"Возраст: {age_info}")

        self.__api.send_message(user_id, info_text)

    def __setup_sex(self, user_id: int, sex_index: int):
        # TODO: add sex preference to UserPreferences table
        global sex_ind # TODO: for testing
        sex_ind = sex_index # TODO: for testing

        sex_name = get_sex_str(sex_index)

        self.__api.send_message(user_id, f"Был установлен пол для поиска - {sex_name}")

    def __setup_region(self, user_id: int, message: str):
        regions = self.__api.get_regions(message)
        if regions:
            region = regions[0]

            # TODO: save region info to db
            global region_name, reg_id  # TODO: for testing
            region_name = region.name  # TODO: for testing
            reg_id = region.id  # TODO: for testing
            ###

            self.__api.send_message(user_id, f"Для поиска был установлен регион {region.name} ✅")
            return True
        else:
            self.__api.send_message(user_id, f"Региона с названием '{message}' не было найдено в базе. "
                                             f"Попробуйте ещё раз, переформулировав название❗")
            return False

    def __setup_city(self, user_id: int, message: str):
        # TODO: get from db region_id
        region_id = reg_id  # TODO: for testing
        ###

        cities = self.__api.get_cities(message, region_id)
        if cities:
            city = cities[0]
            # TODO: save city info to db (city.id, city.name)
            global city_name # TODO: for testing
            city_name = city.name # TODO: for testing
            city_id = city.id # TODO: for testing

            self.__api.send_message(user_id, f"Для поиска был установлен город {city.name} ✅")

        else:
            self.__api.send_message(user_id, f"Города с названием '{message}' не было найдено в базе. "
                                             f"Попробуйте ещё раз, переформулировав название❗")
            return False

        return True

    def __setup_age_from(self, user_id: int, message: str):
        comment = "минимальный возраст"

        age = self.__get_age_from_message(user_id, message, comment)

        if not age:
            return False

        # TODO: save age_from to Preferences table
        global age_from  # TODO: for testing
        age_from = age  # TODO: for testing

        self.__api.send_message(user_id, f"Был установлен {comment} {age} для поиска ✅")

        return True

    def __setup_age_to(self, user_id: int, message: str):
        comment = "максимальный возраст"

        age = self.__get_age_from_message(user_id, message, comment)

        if not age:
            return False

        # TODO: get 'age_from' from Preferences table

        if  age_from > age:
            warn_message = (f"Указан неверный {comment}. "
                            f"Возраст {age} не может быть меньше минимального {age_from}")
            self.__api.send_message(user_id, warn_message)
            return False

        # TODO: save age_to to Preferences table
        global age_to  # TODO: for testing
        age_to = age  # TODO: for testing

        self.__api.send_message(user_id, f"Был установлен {comment} {age} для поиска ✅")

        return True

    def __start_search(self, user_id: int):
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

        self.__api.send_message(user_id, panther_info,
                                search_keyboard,
                                panther_photos)

    def __search_new_panther(self, user_id: int):
        # TODO: get preference user from Preferences table
        # city_id, region_id, sex_index, age_from, age_to = get_from_db_func(user_id) # TODO: insert your realization
        # city_name = get_from_db_func(city_id) # TODO: add
        # region_name = get_from_db_func(region_id) # TODO: add
        global city_id, sex_ind, age_from, age_to, region_id # TODO: for testing
        region_id = reg_id # TODO: for testing
        ###

        user_data = self.__api.search_user(city_id, sex_ind, age_from, age_to)

        # TODO: save candidate to DB (user_data.id, user_data.first_name, user_data.last_name, city_id, region_id)

        user_profile_photos = self.__api.get_photos(user_data.id, "profile")

        user_profile_photos.sort(key=lambda photo: photo.like_count, reverse=True)
        user_profile_photos = user_profile_photos[:QTY_SEND_PROFILE_PHOTOS]
        user_profile_photos = [photo.attachment for photo in user_profile_photos]

        user_mark_photos = self.__api.get_user_mark_photos(user_data.id)

        user_mark_photos.sort(key=lambda photo: photo.like_count, reverse=True)
        user_mark_photos = user_mark_photos[:QTY_SEND_MARK_PHOTOS]
        user_mark_photos = [photo.attachment for photo in user_mark_photos]

        photos_list = user_profile_photos + user_mark_photos

        for photo in photos_list:
            photo.media_id # TODO: save media_id to Photos by user_data.id

        user_location = Location(city_id, city_name, region_id, region_name)

        return user_data, user_location, photos_list

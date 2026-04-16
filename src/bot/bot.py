import os

from src.vk_api.vk_api import API, Events

MAIN_MENU_TEXT = "Вы перешли в главное меню 🏠"

path_keyboard_json_main_menu_structure = (
    os.path.join("src", "vk_api", "keyboard_json_structures", "main_menu.json"))
path_keyboard_json_candidate_select_structure = (
    os.path.join("src", "vk_api", "keyboard_json_structures", "candidate_selection.json"))
path_keyboard_json_candidate_list = (
    os.path.join("src", "vk_api", "keyboard_json_structures", "candidate_list.json"))


class Bot:

    def __init__(self, group_token, user_token, group_id):
        self.__api = API(group_token, user_token, group_id)

    def start(self):
        self.__handler_events()

    def __handler_events(self):
        for event, user_id, data in self.__api.polling_events():
            if event == Events.SEND_MESSAGE:
                ...
            elif event == Events.PUSH_BUTTON:
                if data == "start":
                    self.__add_user_data_preferences(user_id)
                    self.__api.send_message(user_id, MAIN_MENU_TEXT,
                                            path_keyboard_json_main_menu_structure)
                elif data == "start_search":
                    panther_info = self.__search_new_panther(user_id)
                    self.__api.send_message(user_id, panther_info,
                                            path_keyboard_json_candidate_select_structure)
                elif data == "settings_menu":
                    ...
                elif data == "favorites":
                    favorites_info = self.__get_general_people_info_from_favorites(user_id)
                    self.__api.send_message(user_id, favorites_info,
                                            path_keyboard_json_candidate_list)
                elif data == "blacklist":
                    blacklist_info = self.__get_general_people_info_from_blacklist(user_id)
                    self.__api.send_message(user_id, blacklist_info,
                                            path_keyboard_json_candidate_list)
                elif data == "main_menu":
                    self.__api.send_message(user_id, MAIN_MENU_TEXT,
                                            path_keyboard_json_main_menu_structure)

    def __add_user_data_preferences(self, user_id: int):
        # TODO:
        user_data = self.__api.get_info_about_user(user_id)


    def __search_new_panther(self, user_id: int):
        # Version 1
        # # TODO: get preference user from Preferences table
        # # city_id, sex_index, age_from, age_to = get_from_db_func(user_id) # TODO: insert your realization
        # city_id = 1 # example
        # sex_index = 1 # example
        # age_from = 18 # example
        # age_to = 25 # example
        # # Version 2
        # TODO: get user info from DB
        user_data = self.__api.get_info_about_user(user_id) # for example
        city_id = user_data.city.id # example
        sex_index = user_data.sex_index % 2 + 1 # example
        age_from = 20 # example
        age_to = 20 # example
        ###

        user_data = self.__api.search_user(city_id, sex_index, age_from, age_to)

        # TODO: save candidate to DB

        info_text = (f"Была найдена пара 💞:\n"
                     f"- {user_data.first_name}, {user_data.last_name}\n"
                     f"- {user_data.profile_link}")
        return info_text

    @staticmethod
    def __get_general_people_info_from_favorites(user_id: int) -> str:
        # TODO: get general people info list from Favorites table
        # annotation: list[tuple(str, str, str)], example: (Пётр, Тютчев, link-to-vk-profile)
        # people_list = get_from_db_func(user_id) # TODO: insert your realization
        people_list = [("Маша", "Романова", "https://vk.com/id102774978")] # test example
        ###
        info_text = ''
        for person_num, (first_name, last_name, profile_link) in enumerate(people_list, start=1):
            info_text += f"{f'{person_num}.':5} {first_name.capitalize()} {last_name.capitalize()} {profile_link}\n"

        if info_text:
            info_text = "Список избранных ❤️‍🔥:\n" + info_text
        else:
            info_text = "Список избранных пуст 🪹"

        return info_text

    @staticmethod
    def __get_general_people_info_from_blacklist(user_id: int) -> str:
        # TODO: get general people info list from Blacklist table
        # annotation: list[tuple(str, str, str)], example: (Lydia, Makarova, link-to-vk-profile)
        # people_list = get_from_db_func(user_id) # TODO: insert your realization
        people_list = [("Лидия", "Макарова", "https://vk.com/id548929585"),
                       ("Пётр", "Тютчев", "https://vk.com/id731749219")] # test example
        ###
        info_text = ''
        for person_num, (first_name, last_name, profile_link) in enumerate(people_list, start=1):
            info_text += f"{f'{person_num}.':5} {first_name.capitalize()} {last_name.capitalize()} {profile_link}\n"

        if info_text:
            info_text = "Стоп-лист 💔:\n" + info_text
        else:
            info_text = "Стоп-лист пуст 🪹"

        return info_text

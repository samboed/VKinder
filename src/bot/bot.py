from src.bot.base import BotBase
from src.bot.keyboard import (payload_command_keyword, payload_value_keyword,
                              command_go_to_main_menu, command_search_panther,
                              command_show_settings, command_add_sex_prefer, command_show_favorites,
                              command_show_blacklist, command_add_user_to_blacklist,
                              command_add_user_to_favorites, command_show_user_from_blacklist,
                              command_del_user_from_blacklist, command_show_profile_photos_favorites,
                              command_del_user_from_favorites, command_setup_city,
                              command_setup_sex, command_setup_age)
from src.bot.message_processing import BotMessage
from src.bot.partner import BotPartner
from src.bot.setting import BotSetting
from src.bot.show_messages import BotShow
from src.bot.types import DialogStates
from src.vk_api.types import Events


class Bot(BotSetting, BotShow, BotPartner, BotMessage, BotBase):
    def __init__(self, group_token, user_token, group_id, engine):
        BotBase.__init__(self, group_token, user_token, group_id, engine)

    def start(self):
        self.__handler_events()

    def __handler_events(self):
        for event, user_id, payload, event_answer in self._api.polling_events():

            dialog_user_state = self._db.get_dialog_state(user_id)

            if event == Events.SEND_MESSAGE:
                message = payload

                if dialog_user_state == DialogStates.SETUP_REGION:
                    res_setup_region = self._setup_region(user_id, message)
                    if res_setup_region:
                        self._db.update_dialog_state(user_id, DialogStates.SETUP_CITY.value)
                        self._show_city_setup(user_id)

                elif dialog_user_state == DialogStates.SETUP_CITY:
                    res_setup_city = self._setup_city(user_id, message)
                    if res_setup_city:
                        self._db.update_dialog_state(user_id, DialogStates.INITIAL.value)
                        self._show_settings(user_id)

                elif dialog_user_state == DialogStates.SETUP_AGE_FROM:
                    res_setup_age_from = self._setup_age_from(user_id, message)
                    if res_setup_age_from:
                        self._db.update_dialog_state(user_id, DialogStates.SETUP_AGE_TO.value)
                        self._show_age_to_setting(user_id)

                elif dialog_user_state == DialogStates.SETUP_AGE_TO:
                    res_setup_age_to = self._setup_age_to(user_id, message)
                    if res_setup_age_to:
                        self._db.update_dialog_state(user_id, DialogStates.INITIAL.value)
                        self._show_settings(user_id)

                elif dialog_user_state == DialogStates.SHOW_FAVORITE_PHOTO:
                    res_show_favorite_photos = self._show_favorite_photos(user_id, message)
                    if res_show_favorite_photos:
                        self._db.update_dialog_state(user_id, DialogStates.INITIAL.value)

                elif dialog_user_state == DialogStates.SHOW_BLACKLIST_PERSON_PHOTO:
                    res_show_blacklist_photos = self._show_blacklist_person_photos(user_id, message)
                    if res_show_blacklist_photos:
                        self._db.update_dialog_state(user_id, DialogStates.INITIAL.value)

                elif dialog_user_state == DialogStates.DEL_FAVORITE:
                    res_del_favorite = self._del_favorite(user_id, message)
                    if res_del_favorite:
                        self._db.update_dialog_state(user_id, DialogStates.INITIAL.value)
                        self._show_favorites(user_id)

                elif dialog_user_state == DialogStates.DEL_BLACKLIST_PERSON:
                    res_del_blacklist_person = self._del_blacklist_person(user_id, message)
                    if res_del_blacklist_person:
                        self._db.update_dialog_state(user_id, DialogStates.INITIAL.value)
                        self._show_blacklist(user_id)

            elif event == Events.PUSH_BUTTON:
                if payload[payload_command_keyword] == "start":
                    is_new_user = self._db.register_user(user_id)

                    if is_new_user:
                        self._setup_and_show_init_settings(user_id)

                    self._db.update_dialog_state(user_id, DialogStates.INITIAL.value)
                    self._show_main_menu(user_id)

                elif payload[payload_command_keyword] == command_search_panther:
                    self._start_search(user_id)

                elif payload[payload_command_keyword] == command_show_settings:
                    self._show_settings(user_id)

                elif payload[payload_command_keyword] == command_show_favorites:
                    self._show_favorites(user_id)

                elif payload[payload_command_keyword] == command_show_blacklist:
                    self._show_blacklist(user_id)

                elif payload[payload_command_keyword] == command_show_profile_photos_favorites:
                    self._db.update_dialog_state(user_id, DialogStates.SHOW_FAVORITE_PHOTO.value)
                    self._ask_profile_number_for_show_photos_from_favorites(user_id)

                elif payload[payload_command_keyword] == command_show_user_from_blacklist:
                    self._db.update_dialog_state(user_id, DialogStates.SHOW_BLACKLIST_PERSON_PHOTO.value)
                    self._ask_profile_number_for_show_photos_from_blacklist(user_id)

                elif payload[payload_command_keyword] == command_del_user_from_favorites:
                    self._db.update_dialog_state(user_id, DialogStates.DEL_FAVORITE.value)
                    self._ask_profile_number_for_del_from_favorites(user_id)

                elif payload[payload_command_keyword] == command_del_user_from_blacklist:
                    self._db.update_dialog_state(user_id, DialogStates.DEL_BLACKLIST_PERSON.value)
                    self._ask_profile_number_for_del_from_blacklist(user_id)

                elif payload[payload_command_keyword] == command_add_user_to_favorites:
                    self._save_candidate(user_id, payload, self._db.add_to_favorites)
                    self._start_search(user_id)

                elif payload[payload_command_keyword] == command_add_user_to_blacklist:
                    self._save_candidate(user_id, payload, self._db.add_to_blacklist)
                    self._start_search(user_id)

                elif payload[payload_command_keyword] == command_add_sex_prefer:
                    sex = payload[payload_value_keyword]
                    self._setup_sex(user_id, sex)
                    self._show_settings(user_id)

                elif payload[payload_command_keyword] == command_setup_city:
                    self._db.update_dialog_state(user_id, DialogStates.SETUP_REGION.value)
                    self._show_region_setup(user_id)

                elif payload[payload_command_keyword] == command_setup_sex:
                    self._show_sex_setup(user_id)

                elif payload[payload_command_keyword] == command_setup_age:
                    self._db.update_dialog_state(user_id, DialogStates.SETUP_AGE_FROM.value)
                    self._show_age_from_setting(user_id)

                elif payload[payload_command_keyword] == command_go_to_main_menu:
                    self._db.update_dialog_state(user_id, DialogStates.INITIAL.value)
                    self._show_main_menu(user_id)

                if event_answer:
                    self._api.send_message_event_answer(event_answer)

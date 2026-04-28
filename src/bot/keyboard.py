from src.vk_api.keyboard import Button, Keyboard
from src.vk_api.types import Sex, ButtonTypes, ButtonColorTypes

payload_command_keyword = "command"
payload_user_id_keyword = "user_id"
payload_candidate_data_keyword = "candidate_data"
payload_value_keyword = "value"

command_add_sex_prefer = "add_sex_prefer"

command_setup_city = "show_city_prefer"
command_setup_sex = "show_sex_prefer"
command_setup_age = "setup_age_prefer"

command_go_to_main_menu = "main_menu"

command_search_panther = "start_search"

command_show_settings = "show_settings"
command_show_favorites = "show_favorites"
command_show_blacklist = "show_blacklist"

command_add_user_to_blacklist = "add_to_blacklist"
command_add_user_to_favorites = "add_to_favorites"

command_show_profile_photos_favorites = "show_profile_favorite_photos"
command_show_user_from_blacklist = "show_profile_blacklist_photos"

command_del_user_from_favorites = "del_favorite"
command_del_user_from_blacklist = "del_blacklist"

button_main_menu = Button(ButtonTypes.callback,
                          label="Главное меню 🏠",
                          payload={payload_command_keyword: command_go_to_main_menu})

# Sex setting
button_men_sex_preference_select = Button(ButtonTypes.callback,
                                          label="Мужской ♂️",
                                          payload={payload_command_keyword: command_add_sex_prefer,
                                                   payload_value_keyword: Sex.MEN.value},
                                          color=ButtonColorTypes.secondary)
button_women_sex_preference_select = Button(ButtonTypes.callback,
                                            label="Женский ♀️",
                                            payload={payload_command_keyword: command_add_sex_prefer,
                                                     payload_value_keyword: Sex.WOMEN.value},
                                            color=ButtonColorTypes.secondary)
button_all_sex_preference_select = Button(ButtonTypes.callback,
                                          label="Неважно ⚤",
                                          payload={payload_command_keyword: command_add_sex_prefer,
                                                   payload_value_keyword: Sex.ANY.value},
                                          color=ButtonColorTypes.secondary)
button_sex_setup_cancel = Button(ButtonTypes.callback,
                                          label="Отмена ❌",
                                          payload={payload_command_keyword: command_show_settings},
                                          color=ButtonColorTypes.negative)

sex_setting_keyboard = Keyboard([[button_men_sex_preference_select,
                                  button_women_sex_preference_select,
                                  button_all_sex_preference_select],
                                 [button_sex_setup_cancel]])

# Settings menu
button_setup_city = Button(ButtonTypes.callback,
                          label="Изменить город 🏙️",
                          payload={payload_command_keyword: command_setup_city},
                          color=ButtonColorTypes.primary)
button_setup_sex = Button(ButtonTypes.callback,
                          label="Изменить пол ⚤",
                          payload={payload_command_keyword: command_setup_sex},
                          color=ButtonColorTypes.primary)
button_setup_age = Button(ButtonTypes.callback,
                          label="Изменить возраст 🔞",
                          payload={payload_command_keyword: command_setup_age},
                          color=ButtonColorTypes.primary)

settings_menu_keyboard = Keyboard([[button_setup_city], [button_setup_sex], [button_setup_age], [button_main_menu]])

# Main menu
button_search_panther = Button(ButtonTypes.callback,
                               label="Поиск 🔍",
                               payload={payload_command_keyword: command_search_panther},
                               color=ButtonColorTypes.primary)
button_settings = Button(ButtonTypes.callback,
                          label="Настройки ⚙️",
                          payload={payload_command_keyword: command_show_settings},
                          color=ButtonColorTypes.primary)
button_favorites = Button(ButtonTypes.callback,
                          label="Избранные ❤️‍🔥",
                          payload={payload_command_keyword: command_show_favorites},
                          color=ButtonColorTypes.primary)
button_blacklist = Button(ButtonTypes.callback,
                          label="Блэклист 💔",
                          payload={payload_command_keyword: command_show_blacklist},
                          color=ButtonColorTypes.primary)

main_menu_keyboard = Keyboard([[button_search_panther], [button_settings], [button_favorites], [button_blacklist]])

# Casting candidate
button_user_to_blacklist = Button(ButtonTypes.callback,
                                  label="В блэклист 💔",
                                  payload={payload_command_keyword: command_add_user_to_blacklist},
                                  color=ButtonColorTypes.negative)
button_user_to_favorites = Button(ButtonTypes.callback,
                                  label="В избранные ❤️‍🔥",
                                  payload={payload_command_keyword: command_add_user_to_favorites},
                                  color=ButtonColorTypes.positive)

# Favorites
button_show_user_from_favorites = Button(ButtonTypes.callback,
                                         label="Показать фотографии 🖼️",
                                         payload={payload_command_keyword: command_show_profile_photos_favorites},
                                         color=ButtonColorTypes.primary)
button_delete_user_from_favorites = Button(ButtonTypes.callback,
                                           label="Удалить из списка 🗑️",
                                           payload={payload_command_keyword: command_del_user_from_favorites},
                                           color=ButtonColorTypes.primary)

favorites_keyboard = Keyboard([[button_show_user_from_favorites],
                              [button_delete_user_from_favorites],
                              [button_main_menu]])

# Blacklist
button_show_user_from_blacklist = Button(ButtonTypes.callback,
                                         label="Показать фотографии 🖼️",
                                         payload={payload_command_keyword: command_show_user_from_blacklist},
                                         color=ButtonColorTypes.primary)
button_delete_user_from_blacklist = Button(ButtonTypes.callback,
                                           label="Удалить из списка 🗑️",
                                           payload={payload_command_keyword: command_del_user_from_blacklist},
                                           color=ButtonColorTypes.primary)

blacklist_keyboard = Keyboard([[button_show_user_from_blacklist],
                               [button_delete_user_from_blacklist],
                               [button_main_menu]])

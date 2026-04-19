from src.vk_api.types import Sex


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


def get_profile_link(user_id: int):
    return f"https://vk.com/id{user_id}"


def get_user_info_str(user_id: int, first_name: str, last_name: str,
                      city_name: str = '', region_name: str = ''):
    profile_link = get_profile_link(user_id)

    location_str = get_location_str(city_name, region_name)

    info_text = (f"{first_name} {last_name}, {location_str}\n"
                 f"{profile_link}")

    return info_text

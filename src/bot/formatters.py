from src.vk_api.types import Sex, Relation
from src.bot.utils import get_full_age


def get_sex_str(sex_index: int) -> str:
    if sex_index == Sex.MEN.value:
        return "мужчины ♂️"
    elif sex_index == Sex.WOMEN.value:
        return "девушки ♀️"
    else:
        return "мужчины/девушки ⚤"


def get_age_range_str(age_from: int, age_to: int) -> str:
    if age_from == age_to:
        return str(age_from)
    return f"{age_from}-{age_to}"


def get_relation_info_str(relation_ind: int, sex_ind: int) -> str:
    match relation_ind:
        case Relation.NOT_MARRIED.value:
            if sex_ind == Sex.WOMEN.value:
                return "не замужем"
            elif sex_ind == Sex.MEN.value:
                return "не женат"
            return "не в браке"

        case Relation.HAVE_SWEETHEART.value:
            if sex_ind == Sex.MEN.value:
                return "есть подруга"
            return "есть друг"

        case Relation.ENGAGED.value:
            if sex_ind == Sex.WOMEN.value:
                return "помолвлена"
            return "помолвлен"

        case Relation.MARRIED.value:
            if sex_ind == Sex.WOMEN.value:
                return "жената"
            elif sex_ind == Sex.MEN.value:
                return "замужем"
            return "в браке"

        case Relation.COMPLICATED.value:
            return "всё сложно"

        case Relation.IN_ACTIVE_SEARCHING.value:
            return "в активном поиске"

        case Relation.IN_LOVE.value:
            if sex_ind == Sex.WOMEN.value:
                return "влюблена"
            elif sex_ind == Sex.MEN.value:
                return "влюблен"
            return "испытывает влюблённость"

        case Relation.CMN_LAW_MARRIAGE.value:
            return "в гражданском браке"

        case _:
            return ''


def get_location_str(city_name: str, region_name: str = '') -> str:
    if region_name:
        location_info_list = [city_name, region_name]
    else:
        location_info_list = [city_name]

    return ", ".join(location_info_list)


def get_profile_link(user_id: int) -> str:
    return f"https://vk.com/id{user_id}"


def get_user_info_str(user_id: int, first_name: str, last_name: str, bdate: str, city_name: str = '',
                      region_name: str = '', relation: str = None, newline_link=True) -> str:
    profile_link = get_profile_link(user_id)
    location = get_location_str(city_name, region_name)
    age = get_full_age(bdate)

    if relation:
        info_text = f"{first_name} {last_name} ({relation}), {age}, {location}"
    else:
        info_text = f"{first_name} {last_name}, {age}, {location}"

    if newline_link:
        return info_text + f"\n{profile_link}"

    return info_text +  f" {profile_link}"

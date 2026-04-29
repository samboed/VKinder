import random
import sys
import json

from typing import Generator
from urllib.parse import urljoin

from src.vk_api.keyboard import Keyboard
from src.vk_api.service import process_get_request
from src.vk_api.types import User, Attachment, Photo, Region, City, EventAnswer, Events, get_attachment_photo
from src.vk_api.logger import init_logger


URL_BASE = "https://api.vk.ru/method/"

VK_API_VERSION = "5.199"

MAX_BAD_POLLING_REQUEST = 5


class API:
    def __init__(self, group_token: str, user_token: str, group_id: int):
        self.__def_headers = {"Authorization": "Bearer " + group_token}
        self.__user_token = user_token
        self.__group_id = group_id

        init_logger()

    def __setup_long_poll_server_session(self) -> bool:
        url = urljoin(URL_BASE, "groups.setLongPollSettings")

        params = {
            "group_id": self.__group_id,
            "enabled": 1,
            "message_new": 1,
            "message_event": 1,
            "v": VK_API_VERSION
        }

        return process_get_request(url, params, self.__def_headers)

    def __set_long_poll_server_session(self) -> tuple[str, str, str] | bool:
        if not self.__setup_long_poll_server_session():
            return False

        url = urljoin(URL_BASE, "groups.getLongPollServer")

        params = {
            "group_id": self.__group_id,
            "v": VK_API_VERSION
        }

        response_json_data = process_get_request(url, params, self.__def_headers)
        if not response_json_data:
            return False

        session_json_data = response_json_data["response"]

        server = session_json_data["server"]
        key = session_json_data["key"]
        ts = session_json_data["ts"]

        return server, key, ts

    def polling_events(self) -> Generator[tuple[Events, int, str | dict, EventAnswer | None]]:
        res_set_long_poll_server_session = self.__set_long_poll_server_session()
        if not res_set_long_poll_server_session:
            sys.exit(1)

        server, key, ts = res_set_long_poll_server_session

        rest_try_polling_request = MAX_BAD_POLLING_REQUEST
        while rest_try_polling_request:
            url = f"{server}?act=a_check&key={key}&ts={ts}&wait=25&mode=8&version=2"

            response_json_data = process_get_request(url)
            if not response_json_data:
                if not rest_try_polling_request:
                    sys.exit(1)

                rest_try_polling_request -= 1

                continue

            rest_try_polling_request = MAX_BAD_POLLING_REQUEST

            ts = response_json_data["ts"]

            updates = response_json_data["updates"]
            for update in updates:
                event_type = update["type"]

                if event_type == "message_event":
                    user_id = update["object"]["user_id"]
                    event_id = update["object"]["event_id"]
                    peer_id = update["object"]["peer_id"]
                    payload = update["object"]["payload"]

                    event_answer = EventAnswer(user_id, event_id, peer_id)

                    yield Events.PUSH_BUTTON, user_id, payload, event_answer

                elif event_type == "message_new":
                    message = update["object"]["message"]
                    user_id = message["from_id"]

                    if "payload" in message:
                        payload = json.loads(message["payload"])
                        yield Events.PUSH_BUTTON, user_id, payload, None

                    message_text = message["text"]
                    yield Events.SEND_MESSAGE, user_id, message_text, None

    def send_message(self, user_id: int, message: str,
                     keyboard: Keyboard = None,
                     attachments: list[Attachment] = None) -> bool:
        url = urljoin(URL_BASE, "messages.send")

        params = {
            "user_id": user_id,
            "message": message,
            "random_id": random.randint(1, 0xFFFF_FFFF),
            "v": VK_API_VERSION
        }

        if keyboard:
            params["keyboard"] = keyboard.json()
        if attachments:
            attachments_list = []
            for attachment in attachments:
                attachment_text = ''

                if attachment.type:
                    attachment_text += attachment.type
                if attachment.owner_id:
                    attachment_text += str(attachment.owner_id)
                if attachment.media_id:
                    attachment_text += '_' + str(attachment.media_id)

                attachment_text += '_' + self.__user_token

                attachments_list.append(attachment_text)

            params["attachment"] = ",".join(attachments_list)

        return process_get_request(url, params, self.__def_headers)

    def send_message_event_answer(self, event_answer: EventAnswer) -> bool:
        url = urljoin(URL_BASE, "messages.sendMessageEventAnswer")

        params = {
            "user_id": event_answer.user_id,
            "event_id": event_answer.event_id,
            "peer_id": event_answer.peer_id,
            "v": VK_API_VERSION
        }

        return process_get_request(url, params, self.__def_headers)

    def get_regions(self, region_name: str) -> list[Region] | bool:
        url = urljoin(URL_BASE, "database.getRegions")

        params = {
            "access_token": self.__user_token,
            "q": region_name,
            "v": VK_API_VERSION
        }

        response_json_data = process_get_request(url, params=params)
        if not response_json_data:
            return False

        regions_json_data = response_json_data["response"]

        regions = []
        for region_item in regions_json_data["items"]:
            regions.append(Region(region_item["id"], region_item["title"]))

        return regions

    def get_cities(self, city_name: str = None,
                   region_id: int = None) -> list[City] | bool:
        url = urljoin(URL_BASE, "database.getCities")

        params = {
            "access_token": self.__user_token,
            "need_all": 1,
            "v": VK_API_VERSION
        }

        if city_name:
            params["q"] = city_name

        if region_id:
            params["region_id"] = region_id

        response_json_data = process_get_request(url, params=params)
        if not response_json_data:
            return False

        cities_json_data = response_json_data["response"]

        cities = []
        for city_item in cities_json_data["items"]:
            city_id = city_item["id"]
            city_name = city_item["title"]

            city_area = ''
            city_region = ''
            if "area" in city_item:
                city_area = city_item["area"]
            if "region" in city_item:
                city_region = city_item["region"]

            city = City(city_id, city_name, city_area, city_region)

            cities.append(city)

        return cities

    def get_info_about_user(self, user_id: int) -> User | bool:
        url = urljoin(URL_BASE, "users.get")

        params = {
            "user_ids": user_id,
            "fields": ",".join(["city", "bdate", "sex"]),
            "v": VK_API_VERSION
        }

        response_json_data = process_get_request(url, params, self.__def_headers)
        if not response_json_data:
            return False

        user_json_data = response_json_data["response"][0]

        first_name = user_json_data["first_name"]
        last_name = user_json_data["last_name"]
        city = user_json_data.get("city")
        if city:
            city_id = user_json_data["city"]["id"]
            city_name = user_json_data["city"]["title"]
        else:
            city_id = None
            city_name = ''
        if "bdate" in user_json_data:
            birthday_date = user_json_data["bdate"]
        else:
            birthday_date = ""
        sex_index = user_json_data["sex"]
        is_closed = user_json_data["is_closed"]

        user_data = User(user_id, first_name, last_name,
                         City(city_id, city_name, '', ''),
                         birthday_date, sex_index, '', is_closed)

        return user_data

    def get_photos(self, owner_id: int, album_name: str) -> list[Photo] | bool:
        url = urljoin(URL_BASE, "photos.get")

        params = {
            "access_token": self.__user_token,
            "owner_id": owner_id,
            "album_id": album_name,
            "rev": 1,
            "extended": 1,
            "v": VK_API_VERSION
        }

        response_json_data = process_get_request(url, params=params)
        if not response_json_data:
            return False

        photos_json_data = response_json_data["response"]["items"]

        photos_list = []
        for item in photos_json_data:
            photo_id = item["id"]
            qty_likes = item["likes"]["count"]

            photos_list.append(Photo(get_attachment_photo(owner_id, photo_id), qty_likes))

        return photos_list

    def get_user_mark_photos(self, user_id: int) -> list[Photo] | bool:
        url = urljoin(URL_BASE, "photos.getUserPhotos")

        params = {
            "access_token": self.__user_token,
            "user_id": user_id,
            "extended": 1,
            "sort": 0,
            "v": VK_API_VERSION
        }

        response_json_data = process_get_request(url, params=params)
        if not response_json_data:
            return False

        photos_json_data = response_json_data["response"]["items"]

        photos_list = []
        for item in photos_json_data:
            owner_id = item["owner_id"]
            photo_id = item["id"]
            qty_likes = item["likes"]["count"]

            photos_list.append(Photo(get_attachment_photo(owner_id, photo_id), qty_likes))

        return photos_list

    def search_users(self, city_id: int, sex_index: int,
                     age_from: int, age_to: int, offset_search: int = 0,
                     can_be_private_profile: bool = False) -> list[User] | bool:
        url = urljoin(URL_BASE, "users.search")

        params = {
            "access_token": self.__user_token,
            "city": city_id,
            "sex": sex_index,
            "age_from": age_from,
            "age_to": age_to,
            "offset": offset_search,
            "sort": 1,
            "online": 0,
            "has_photo": 1,
            "count": 1000,
            "fields": "bdate,relation,sex",
            "v": VK_API_VERSION
        }

        response_json_data = process_get_request(url, params)
        if not response_json_data:
            return False

        searched_users_json_data = response_json_data["response"]["items"]

        users = []
        for searched_user_json_data in searched_users_json_data:
            is_closed = searched_user_json_data["is_closed"]

            if not can_be_private_profile and is_closed:
                continue

            user_id = searched_user_json_data["id"]
            first_name = searched_user_json_data["first_name"]
            last_name = searched_user_json_data["last_name"]
            bdate = searched_user_json_data["bdate"]
            relation_index = searched_user_json_data.get("relation", 0)
            sex_index = searched_user_json_data["sex"]

            users.append(User(user_id, first_name, last_name, '', bdate, sex_index, relation_index, ''))

        return users

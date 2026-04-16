import random
import requests
import json

from enum import Enum
from collections import namedtuple
from urllib.parse import urljoin


URL_BASE = "https://api.vk.ru/method/"

VK_API_VERSION = "5.199"


# TODO: abstract class for keyboard


class Events(Enum):
    SEND_MESSAGE = 1
    PUSH_BUTTON = 2


class API:
    def __init__(self, group_token: str, user_token: str, group_id: int):
        self.__def_headers = {"Authorization": group_token}
        self.__user_token = user_token
        self.__group_id = group_id


    def __setup_long_poll_server_session(self):
        url = urljoin(URL_BASE, "groups.setLongPollSettings")
        params = {
            "group_id": self.__group_id,
            "v": VK_API_VERSION,
            "enabled": 1,
            "message_new": 1,
            "message_event": 1
        }
        response = requests.get(url, headers=self.__def_headers, params=params)

        # TODO: add handle errors

    def __set_long_poll_server_session(self):
        url = urljoin(URL_BASE, "groups.getLongPollServer")
        params = {
            "group_id": self.__group_id,
            "v": VK_API_VERSION
        }

        response = requests.get(url, headers=self.__def_headers, params=params)

        # TODO: add handle errors

        session_json_data = response.json()["response"]

        server = session_json_data["server"]
        key = session_json_data["key"]
        ts = session_json_data["ts"]

        return server, key, ts

    def polling_events(self):
        server, key, ts = self.__set_long_poll_server_session()
        while True:
            url = f"{server}?act=a_check&key={key}&ts={ts}&wait=25&mode=8&version=2"
            response = requests.get(url)
            data = response.json()
            ts = data["ts"]
            updates = data["updates"]
            for update in updates:
                event_type = update["type"]
                if event_type == "message_event":
                    user_id = update["object"]["user_id"]
                    event_id = update["object"]["event_id"]
                    peer_id = update["object"]["peer_id"]
                    command = update["object"]["payload"]["command"]
                    self.__send_message_event_answer(event_id, user_id, peer_id)
                    yield Events.PUSH_BUTTON, user_id, command
                elif event_type == "message_new":
                    user_id = update["object"]["message"]["from_id"]
                    message = update["object"]["message"]["text"]
                    payload = json.loads(update["object"]["message"]["payload"])
                    if payload:
                        yield Events.PUSH_BUTTON, user_id, payload["command"]
                    yield Events.SEND_MESSAGE, user_id, message

    def send_message(self, user_id: int, message: str,
                     path_to_keyboard_json_structure: str, attachments: list[str] = None):
        with open(path_to_keyboard_json_structure, encoding="utf-8") as json_file:
            keyboard_structure_json = json_file.read()

        url = urljoin(URL_BASE, "messages.send")
        params = {
            "user_id": user_id,
            "message": message,
            "random_id": random.randint(1, 0xFFFF_FFFF),
            "keyboard": keyboard_structure_json,
            "v": VK_API_VERSION
        }
        if attachments:
            params["attachment"] = ",".join(attachments)

        response = requests.get(url, params, headers=self.__def_headers)

        # TODO: add handle errors

    def get_info_about_user(self, user_id: int):
        url = urljoin(URL_BASE, "users.get")

        params = {
            "user_ids": user_id,
            "fields": ",".join(["city", "bdate", "sex"]),
            "v": VK_API_VERSION
        }

        response = requests.get(url, params, headers=self.__def_headers)

        # TODO: add handle errors

        user_json_data = response.json()["response"][0]

        first_name = user_json_data["first_name"]
        last_name = user_json_data["last_name"]
        city_id = user_json_data["city"]["id"]
        city_name = user_json_data["city"]["title"]
        birthday_date = user_json_data["bdate"]
        sex_index = user_json_data["sex"]
        is_closed = user_json_data["is_closed"]

        City = namedtuple("City", ["id", "name"])
        User = namedtuple('User',
                          ["first_name", "last_name", "city", "bdate", "sex_index", "is_closed"])

        user_data = User(first_name, last_name, City(city_id, city_name), birthday_date, sex_index, is_closed)

        return user_data

    def search_user(self, city_id: int, sex_index: int, age_from: int, age_to: int):
        url = urljoin(URL_BASE, "users.search")

        params = {
            "access_token": self.__user_token,
            "city": city_id,
            "sex": sex_index,
            "age_from": age_from,
            "age_to": age_to,
            "is_closed": False,
            "status": 6,
            "count": 1000,
            "v": VK_API_VERSION
        }

        response = requests.get(url, params)

        # TODO: add handle errors

        searched_user_json_data = response.json()["response"]['items'][random.randint(0, 100)]

        user_id = searched_user_json_data["id"]
        first_name = searched_user_json_data["first_name"]
        last_name = searched_user_json_data["last_name"]
        profile_link = f"https://vk.com/id{user_id}"

        User = namedtuple('User',
                          ["user_id", "first_name", "last_name", "profile_link"])

        user = User(user_id, first_name, last_name, profile_link)

        return user

    def __send_message_event_answer(self, event_id: int, user_id:int, peer_id:int):
        url = urljoin(URL_BASE, "messages.sendMessageEventAnswer")

        params = {
            "event_id": event_id,
            "user_id": user_id,
            "peer_id": peer_id,
            "v": VK_API_VERSION
        }

        response = requests.get(url, params, headers=self.__def_headers)

        # TODO: add handle errors

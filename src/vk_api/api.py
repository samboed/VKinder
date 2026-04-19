import random
import requests
import json

from collections import namedtuple
from urllib.parse import urljoin

from src.vk_api.keyboard import Keyboard
from src.vk_api.types import Attachment, Photo, Events

URL_BASE = "https://api.vk.ru/method/"

VK_API_VERSION = "5.199"


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

    def get_attachment_photo(self, user_id: int, media_id: int):
        return Attachment("photo", user_id, media_id, self.__user_token)

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
                    payload = update["object"]["payload"]
                    self.__send_message_event_answer(event_id, user_id, peer_id)
                    yield Events.PUSH_BUTTON, user_id, payload
                elif event_type == "message_new":
                    message = update["object"]["message"]
                    user_id = message["from_id"]
                    if "payload" in message:
                        payload = json.loads(message["payload"])
                        yield Events.PUSH_BUTTON, user_id, payload
                    message_text = message["text"]
                    yield Events.SEND_MESSAGE, user_id, message_text

    def send_message(self, user_id: int, message: str,
                     keyboard: Keyboard = None, attachments: list[Attachment] = None):
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
                if attachment.access_key:
                    attachment_text += '_' + attachment.access_key

                attachments_list.append(attachment_text)

            params["attachment"] = ",".join(attachments_list)

        response = requests.get(url, params, headers=self.__def_headers)

        # TODO: add handle errors

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

    def get_regions(self, region_name: str):
        url = urljoin(URL_BASE, "database.getRegions")

        params = {
            "access_token": self.__user_token,
            "q": region_name,
            "v": VK_API_VERSION
        }

        response = requests.get(url, params)

        # TODO: add handle errors

        regions_json_data = response.json()["response"]

        Region = namedtuple("Region", ["id", "name"])

        regions = []
        for region_item in regions_json_data["items"]:
            regions.append(Region(region_item["id"], region_item["title"]))

        return regions

    def get_cities(self, city_name: str = None, region_id: int = None):
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



        response = requests.get(url, params)

        # TODO: add handle errors

        cities_json_data = response.json()["response"]

        City = namedtuple("City", ["id", "name", "area", "region"], defaults='')

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
        if "bdate" in user_json_data:
            birthday_date = user_json_data["bdate"]
        else:
            birthday_date = ""
        sex_index = user_json_data["sex"]
        is_closed = user_json_data["is_closed"]

        City = namedtuple("City", ["id", "name"])
        User = namedtuple('User',
                          ["first_name", "last_name", "city", "bdate", "sex_index", "is_closed"])

        user_data = User(first_name, last_name, City(city_id, city_name), birthday_date, sex_index, is_closed)

        return user_data

    def get_photos(self, owner_id: int, album_name: str):
        url = urljoin(URL_BASE, "photos.get")

        params = {
            "access_token": self.__user_token,
            "owner_id": owner_id,
            "album_id": album_name,
            "rev": 1,
            "extended": 1,
            "v": VK_API_VERSION
        }

        response = requests.get(url, params)

        # TODO: add handle errors
        if "error" in response.json():
            return []

        photos_json_data = response.json()["response"]["items"]

        photos_list = []
        for item in photos_json_data:
            qty_likes = item["likes"]["count"]
            photo_id = item["id"]
            photos_list.append(Photo(self.get_attachment_photo(owner_id, photo_id), qty_likes))

        return photos_list

    def get_user_mark_photos(self, user_id: int):
        url = urljoin(URL_BASE, "photos.getUserPhotos")

        params = {
            "access_token": self.__user_token,
            "user_id": user_id,
            "extended": 1,
            "sort": 0,
            "v": VK_API_VERSION
        }

        response = requests.get(url, params)

        # TODO: add handle errors
        if "error" in response.json():
            return []

        photos_json_data = response.json()["response"]["items"]

        photos_list = []
        for item in photos_json_data:
            qty_likes = item["likes"]["count"]
            photo_id = item["id"]
            photos_list.append(Photo(self.get_attachment_photo(user_id, photo_id), qty_likes))

        return photos_list

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

        User = namedtuple('User',
                          ["id", "first_name", "last_name"])

        user = User(user_id, first_name, last_name)

        return user
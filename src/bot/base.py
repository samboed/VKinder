from src.vk_api.api import API


class BotBase:
    def __init__(self, group_token, user_token, group_id):
        self._api = API(group_token, user_token, group_id)

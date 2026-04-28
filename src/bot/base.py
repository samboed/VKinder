from sqlalchemy.engine.base import Engine

from src.db.db_manager import DatabaseManager
from src.vk_api.api import API


class BotBase:
    def __init__(self, group_token: str, group_id: int,
                 user_token: str, engine: Engine):
        self._api = API(group_token, user_token, group_id)
        self._db = DatabaseManager(engine)

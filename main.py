import os
import sqlalchemy as sq

from dotenv import load_dotenv

from src.db.database import create_tables
from src.bot.bot import Bot


load_dotenv()

TOKEN_GROUP = os.getenv("TOKEN_GROUP")
TOKEN_USER = os.getenv("TOKEN_USER")
GROUP_ID = os.getenv("VK_GROUP_ID")
DSN = os.getenv("DSN")


if __name__ == "__main__":
    if not DSN:
        raise ValueError("DSN не найден. Убедитесь, что файл .env настроен.")

    engine = sq.create_engine(DSN)
    create_tables(engine)

    bot = Bot(TOKEN_GROUP, TOKEN_USER, GROUP_ID, engine)
    bot.start()
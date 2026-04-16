from src.bot.bot import Bot

import os

TOKEN_GROUP = os.getenv("TOKEN_GROUP")
TOKEN_USER = os.getenv("TOKEN_USER")
GROUP_ID = os.getenv("VK_GROUP_ID")


if __name__ == "__main__":
    bot = Bot(TOKEN_GROUP, TOKEN_USER, GROUP_ID)
    bot.start()
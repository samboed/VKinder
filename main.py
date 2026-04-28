from src.settings import load_env_variables
from src.db.database import create_tables, create_engine
from src.bot.bot import Bot


if __name__ == "__main__":
    token_group, group_id, token_user, dsn = load_env_variables()

    engine = create_engine(dsn)

    create_tables(engine)

    bot = Bot(token_group, group_id, token_user, engine)
    bot.start()
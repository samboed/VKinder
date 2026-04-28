import os
import sys

from dotenv import load_dotenv


def load_env_variables() -> tuple[str, int, str, str]:
    load_dotenv()

    token_group = os.getenv("TOKEN_GROUP")
    group_id = os.getenv("GROUP_ID")
    token_user = os.getenv("TOKEN_USER")
    dsn = os.getenv("DSN")

    res = True

    if not token_group:
        res = False
        print("'TOKEN_GROUP' isn't defined! "
              "Please define 'TOKEN_GROUP' environment variable in .env file",
              file=sys.stderr)

    if not group_id:
        res = False
        print("'GROUP_ID' isn't defined! "
              "Please define 'GROUP_ID' environment variable in .env file",
              file=sys.stderr)

    if not token_user:
        res = False
        print("'TOKEN_USER' isn't defined! "
              "Please define 'TOKEN_USER' environment variable in .env file",
              file=sys.stderr)

    if not dsn:
        res = False
        print("'DSN' isn't defined! "
              "Please define 'DSN' environment variable in .env file",
              file=sys.stderr)

    if not res:
        sys.exit(0)

    return token_group, group_id, token_user, dsn

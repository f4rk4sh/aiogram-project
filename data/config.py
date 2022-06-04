import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = str(os.getenv("TOKEN"))

ADMINS = [int(admin_id) for admin_id in os.getenv("ADMINS").split(",")]

POSTGRES_HOST = str(os.getenv("POSTGRES_HOST"))
POSTGRES_USER = str(os.getenv("POSTGRES_USER"))
POSTGRES_PASSWORD = str(os.getenv("POSTGRES_PASSWORD"))
POSTGRES_DB = str(os.getenv("POSTGRES_DB"))

POSTGRES_URI = (
    f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
)

TORTOISE_ORM = {
    "connections": {"default": POSTGRES_URI},
    "apps": {
        "models": {
            "models": ["utils.db_api.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

REDIS_HOST = str(os.getenv("REDIS_HOST"))
REDIS_DB = int(os.getenv("REDIS_DB"))
REDIS_PORT = int(os.getenv("REDIS_PORT"))

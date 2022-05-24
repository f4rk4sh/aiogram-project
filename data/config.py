import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = str(os.getenv('TOKEN'))

ADMINS = [int(admin_id) for admin_id in os.getenv('ADMINS').split(',')]
MASTERS = [int(master_id) for master_id in os.getenv('MASTERS').split(',')]

POSTGRES_HOST = str(os.getenv('POSTGRES_HOST'))
POSTGRES_USER = str(os.getenv('POSTGRES_USER'))
POSTGRES_PASSWORD = str(os.getenv('POSTGRES_PASSWORD'))
POSTGRES_DB = str(os.getenv('POSTGRES_DB'))

POSTGRES_URI = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}'

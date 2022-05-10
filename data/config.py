import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = str(os.getenv('TOKEN'))

ADMINS = [int(admin_id) for admin_id in os.getenv('ADMINS').split(',')]
MASTERS = [int(master_id) for master_id in os.getenv('MASTERS').split(',')]

PG_HOST = str(os.getenv('PG_HOST'))
PG_USER = str(os.getenv('PG_USER'))
PG_PASSWORD = str(os.getenv('PG_PASSWORD'))
PG_DATABASE = str(os.getenv('PG_DATABASE'))

POSTGRES_URI = f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/{PG_DATABASE}'

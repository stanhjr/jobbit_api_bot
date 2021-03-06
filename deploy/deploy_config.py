import os

from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv('TOKEN')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_PORT = os.getenv('DATABASE_PORT') or 5432
DATABASE_URL = f'postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'

JOBBIT_API_HOSTNAME = os.getenv('JOBBIT_API_HOSTNAME')
JOBBIT_API_TELEGRAM_BOT_TOKEN = os.getenv('JOBBIT_API_TELEGRAM_BOT_TOKEN')







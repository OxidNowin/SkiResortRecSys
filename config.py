# - *- coding: utf- 8 - *-
import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_KEY')
DB_NAME = os.getenv('DB_NAME')
USER = os.getenv('USER_BD')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
BOT_ADMIN = os.getenv('BOT_ADMIN')

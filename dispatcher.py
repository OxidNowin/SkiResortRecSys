# - *- coding: utf- 8 - *-
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config


logging.basicConfig(level=logging.INFO)

if not config.BOT_TOKEN:
    exit("No token provided")

storage = MemoryStorage()
bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")

dp = Dispatcher(bot, storage=storage)

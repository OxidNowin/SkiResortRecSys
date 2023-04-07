# - *- coding: utf- 8 - *-
import filters
from aiogram import executor
from dispatcher import dp
import handlers
from utils import create_db
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    create_db.create_tables()
    filters.setup(dispatcher)

    await set_default_commands(dispatcher)

    print("~~~~~ Bot was started ~~~~~")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

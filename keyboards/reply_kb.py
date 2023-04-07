# - *- coding: utf- 8 - *-
from aiogram import types


start_reply_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
start_reply_kb.row('📖 Подбор горнолыжного курорта по описанию')
start_reply_kb.row('📖 Подбор горнолыжного курорта по параметрам')
start_reply_kb.row('🔥 О нас')

cancel_reply_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
cancel_reply_kb.row('⛔ Отмена')

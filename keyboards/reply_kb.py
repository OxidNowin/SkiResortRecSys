# - *- coding: utf- 8 - *-
from aiogram import types


start_reply_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
start_reply_kb.row('📖 Подбор горнолыжного курорта по описанию')
start_reply_kb.row('📖 Подбор горнолыжного курорта по параметрам')
start_reply_kb.row('🔥 О нас')

estimate_reply_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
estimate_reply_kb.row('1', '2', '3')
estimate_reply_kb.row('4', '5', '6')
estimate_reply_kb.row('7', '8', '9')
estimate_reply_kb.row('10')
estimate_reply_kb.row('⛔ Отмена')

duration_reply_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
duration_reply_kb.row('На 2..4 ночи')
duration_reply_kb.row('На неделю')
duration_reply_kb.row('На 10 ночей')
duration_reply_kb.row('На 2 недели')
duration_reply_kb.row('⛔ Отмена')

cancel_reply_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
cancel_reply_kb.row('⛔ Отмена')

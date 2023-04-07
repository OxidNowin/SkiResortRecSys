# - *- coding: utf- 8 - *-
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hlink

from dispatcher import dp
from filters import IsAdmin
from keyboards import *
from utils import is_user, add_user
from states import OpenQuestion
from utils.openai_api.openai import get_resort

import logging
import datetime
import re


DATE_REGEX = r'^(0[1-9]|[1-2][0-9]|3[0-1])[/\-.](0[1-9]|1[0-2])[/\-.]([0-9]{4})$'


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    ans = f"Привет, {message.from_user.first_name.title()}\n"
    if not await is_user(message.from_user.id):
        await add_user(message.from_user.id, message.from_user.username)
        ans += "Я бот для подбора горнолыжных курортов в России!\n"
    else:
        ans += 'Рады снова тебя видеть!'
    await message.bot.send_message(message.chat.id, ans, reply_markup=start_reply_kb)


@dp.message_handler(commands=['menu'])
async def menu(message: types.Message):
    await message.bot.send_message(message.chat.id, "Главное меню:", reply_markup=start_reply_kb)


@dp.message_handler(Text(equals='📖 Подбор горнолыжного курорта по описанию'))
async def open_question(message: types.Message):
    await OpenQuestion.vacation_start.set()
    await message.bot.send_message(message.chat.id,
                                   "Укажите временной промежуток в формате день.месяц.год-день.месяц.год "
                                   "когда бы Вы хотели съездить на курорт",
                                   reply_markup=cancel_reply_kb)


@dp.message_handler(Text(equals='📖 Подбор горнолыжного курорта по параметрам'))
async def close_question(message: types.Message):
    await message.bot.send_message(message.chat.id, "В разработке...", reply_markup=start_reply_kb)


@dp.message_handler(state='*', commands='⛔ Отмена')
@dp.message_handler(Text(equals='⛔ Отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info(f'From {message.from_user.id}\n'
                 f'Cancelling state {current_state}\n'
                 f'At {datetime.datetime.now()}\n\n')
    await state.finish()
    await message.reply('Отмена...', reply_markup=start_reply_kb)


@dp.message_handler(state=OpenQuestion.vacation_start)
async def vacation_date_close_question(message: types.Message, state: FSMContext):
    try:
        start, end = message.text.split('-')
        if not (re.match(DATE_REGEX, start.strip()) and re.match(DATE_REGEX, start.strip())):
            raise ValueError
    except ValueError:
        await message.bot.send_message(message.chat.id,
                                       "Введите временной промежуток в формате день.месяц.год-день.месяц.год!\n"
                                       "Например: 12.12.2023-20.12.2023",
                                       reply_markup=cancel_reply_kb)
        return
    await state.update_data(vacation_start=start)
    await state.update_data(vacation_end=end)
    await OpenQuestion.request.set()
    await message.bot.send_message(message.chat.id,
                                   "Опишите в подробностях Ваш предполагаемый отдых?",
                                   reply_markup=cancel_reply_kb)


@dp.message_handler(state=OpenQuestion.request)
async def request_close_question(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        start = data['vacation_start']
        end = data['vacation_end']
    await state.finish()
    msq_to_ai = f"Подбери 1 горнолыжный курорт в России на даты {start}-{end}, " \
                f"удовлетворяющий следующему запросу:{message.text}"
    response = await get_resort(msq_to_ai)
    await message.bot.send_message(message.chat.id,
                                   response,
                                   reply_markup=start_reply_kb)

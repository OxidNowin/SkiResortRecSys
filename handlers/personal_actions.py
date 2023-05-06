# - *- coding: utf- 8 - *-
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hlink

from dispatcher import dp
from filters import IsAdmin
from keyboards import *
from utils import is_user, add_user, add_finding
from states import OpenQuestion, CloseQuestion
from utils.openai_api.openai import get_resort
from utils.agregator import get_tour

import logging
import datetime
import re


DATE_REGEX = r'^(0[1-9]|[1-2][0-9]|3[0-1])[/.](0[1-9]|1[0-2])[/.]([0-9]{4})$'


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
    await CloseQuestion.vacation_start.set()
    await message.bot.send_message(message.chat.id,
                                   "Укажите дату начала вашего в формате день.месяц.год "
                                   "когда бы Вы хотели съездить на курорт",
                                   reply_markup=cancel_reply_kb)


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
async def vacation_date_open_question(message: types.Message, state: FSMContext):
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
async def request_open_question(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        start = data['vacation_start']
        end = data['vacation_end']
    msq_to_ai = f"Подбери 1 горнолыжный курорт на даты {start}-{end}, " \
                f"удовлетворяющий следующему запросу:\n{message.text}"
    await message.bot.send_message(message.chat.id,
                                   'Подбираем горнолыжный курорт...',
                                   reply_markup=start_reply_kb)
    response, time = await get_resort(msq_to_ai)
    await state.update_data(response_time=time)
    await OpenQuestion.estimate.set()
    await message.bot.send_message(message.chat.id,
                                   response)
    await message.bot.send_message(message.chat.id,
                                   'Поставьте оценку предложенного нами курорта',
                                   reply_markup=estimate_reply_kb)


@dp.message_handler(state=OpenQuestion.estimate)
async def request_estimate(message: types.Message, state: FSMContext):
    if isinstance(int(message.text), int):
        if not(1 <= int(message.text) <= 10):
            await message.bot.send_message(message.chat.id,
                                           'Поставьте оценку от 1 до 10',
                                           reply_markup=estimate_reply_kb)
            return
    else:
        await message.bot.send_message(message.chat.id,
                                       'Поставьте оценку от 1 до 10',
                                       reply_markup=estimate_reply_kb)
        return
    async with state.proxy() as data:
        time = data['response_time']
    await state.finish()
    await add_finding(message.from_user.id, int(message.text), time, True)
    await message.bot.send_message(message.chat.id,
                                   'Спасибо что выбрали наш сервис по подбору горнолыжный курортов!',
                                   reply_markup=start_reply_kb)


@dp.message_handler(state=CloseQuestion.vacation_start)
async def vacation_start_date_close_question(message: types.Message, state: FSMContext):
    try:
        if not re.match(DATE_REGEX, message.text.strip()):
            raise ValueError
        else:
            start = datetime.datetime.strptime(message.text.strip(), '%d.%m.%Y')
    except ValueError:
        await message.bot.send_message(message.chat.id,
                                       "Введите дату начала отдыха в формате день.месяц.год!\n"
                                       "Например: 12.12.2023",
                                       reply_markup=cancel_reply_kb)
        return
    await state.update_data(vacation_start=start)
    await CloseQuestion.vacation_end.set()
    await message.bot.send_message(message.chat.id,
                                   "Выберите продолжительность указав дату в формате день.месяц.год\n"
                                   "Либо выберите продолжиительность с клавиатурыы",
                                   reply_markup=duration_reply_kb)


@dp.message_handler(state=CloseQuestion.vacation_end)
async def vacation_end_date_close_question(message: types.Message, state: FSMContext):
    try:
        if not re.match(DATE_REGEX, message.text.strip()):
            if message.text not in ['На 2..4 ночи', 'На неделю', 'На 10 ночей', 'На 2 недели']:
                raise ValueError
            else:
                if message.text == 'На 2..4 ночи':
                    nights = 'mini'
                elif message.text == 'На неделю':
                    nights = 'week'
                elif message.text == 'На 10 ночей':
                    nights = 'ten_nights'
                else:
                    nights = 'two_weeks'
        else:
            async with state.proxy() as data:
                start = data['vacation_start']
            nights = (datetime.datetime.strptime(message.text.strip(), '%d.%m.%Y') - start).days
    except ValueError:
        await message.bot.send_message(message.chat.id,
                                       "Введите дату конца отдыха в формате день.месяц.год!\n"
                                       "Например: 12.12.2023",
                                       reply_markup=duration_reply_kb)
        return

    await state.update_data(nights=nights)
    await CloseQuestion.adults.set()
    await message.bot.send_message(message.chat.id,
                                   "Введите количество взрослых человек",
                                   reply_markup=cancel_reply_kb)


@dp.message_handler(state=CloseQuestion.adults)
async def adults_amount(message: types.Message, state: FSMContext):
    if not(1 <= int(message.text) <= 5):
        await message.bot.send_message(message.chat.id,
                                       'Введите количество от 1 до 5',
                                       reply_markup=cancel_reply_kb)
        return

    await state.update_data(adults=int(message.text))
    await CloseQuestion.filter_stars.set()
    await message.bot.send_message(message.chat.id,
                                   "Введите количество звёзд в отеле",
                                   reply_markup=cancel_reply_kb)


@dp.message_handler(state=CloseQuestion.filter_stars)
async def hotel_stars(message: types.Message, state: FSMContext):
    if not(1 <= int(message.text) <= 5):
        await message.bot.send_message(message.chat.id,
                                       'Введите количество от 1 до 5',
                                       reply_markup=cancel_reply_kb)
        return

    await state.update_data(filter_stars=int(message.text))
    async with state.proxy() as data:
        adults = data['adults']
        nights = data['nights']
        d, m, y = datetime.datetime.strftime(data['vacation_start'], '%d.%m.%Y').split('.')
        start = f'{y}-{m}-{d}'
        star = data['filter_stars']
    await state.finish()
    data = await get_tour(adults, nights, start, star)
    if data:
        msg = f"Мы нашли для вас тур в {data['hotel']['city']}!\n\n" \
              f"{data['hotel']['desc']}\n" \
              f"Стоимость: {data['min_price']} руб.\n" \
              f"Апартаменты: {data['hotel']['name']}"
    else:
        msg = 'К сожалению, туров по заданым параметрам не удалось найти'
    await message.bot.send_message(message.chat.id,
                                   msg,
                                   reply_markup=start_reply_kb)

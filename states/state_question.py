# - *- coding: utf- 8 - *-
from aiogram.dispatcher.filters.state import State, StatesGroup


class OpenQuestion(StatesGroup):
    vacation_start = State()
    vacation_end = State()
    request = State()
    estimate = State()
    response_time = State()


class CloseQuestion(StatesGroup):
    vacation_start = State()
    vacation_end = State()
    adults = State()
    kids = State()
    filter_stars = State()
    nights = State()

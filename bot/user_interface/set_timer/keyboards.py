from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from database.database import db


async def get_timers_keyboard():
    keyboard = [
        [InlineKeyboardButton(text='5 минут', callback_data='set_timer|5')],
        [InlineKeyboardButton(text='10 минут', callback_data='set_timer|10')],
        [InlineKeyboardButton(text='20 минут', callback_data='set_timer|20')],
        [InlineKeyboardButton(text='Свой промежуток', callback_data='set_timer_self')],
        [InlineKeyboardButton(text='Назад', callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
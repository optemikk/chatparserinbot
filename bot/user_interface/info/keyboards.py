from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from database.database import db


async def get_info_kb():
    keyboard = [
        [InlineKeyboardButton(text='Назад', callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

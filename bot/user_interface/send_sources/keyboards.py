from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from database.database import db


async def get_cancel_send_sources_kb():
    keyboard = [
        [InlineKeyboardButton(text='Назад', callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_add_another_sources_kb():
    keyboard = [
        [InlineKeyboardButton(text='Добавить еще', callback_data='send_source')],
        [InlineKeyboardButton(text='Назад', callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

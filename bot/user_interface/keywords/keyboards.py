from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from database.database import db


async def get_main_keyword_kb():
    keyboard = [
        [InlineKeyboardButton(text='Список слов', callback_data='keyword_list')],
        [InlineKeyboardButton(text='Список стоп-слов', callback_data='stop_keyword_list')],
        [InlineKeyboardButton(text='Назад', callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_add_keywords_kb(is_stop: bool, is_empty: bool):
    keyboard = [
        [InlineKeyboardButton(text='Добавить слова', callback_data=f'add_{"stop_" if is_stop else ""}keyword')],
        [InlineKeyboardButton(text='Назад', callback_data='keywords')]
    ]
    if not is_empty:
        keyboard.insert(1, [InlineKeyboardButton(text='Удалить все слова', callback_data=f'delete_all_{"stop_" if is_stop else ""}keywords')])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_cancel_adding_keyword_kb(is_stop: bool):
    keyboard = [
        [InlineKeyboardButton(text='Назад', callback_data=f'{"stop_" if is_stop else ""}keyword_list')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_check_add_words_kb(is_stop: bool):
    keyboard = [
        [InlineKeyboardButton(text='Да', callback_data=f'add_{"stop_" if is_stop else ""}keyword')],
        [InlineKeyboardButton(text='Нет', callback_data=f'{"stop_" if is_stop else ""}keyword_list')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def is_word_required(is_stop: bool):
    keyboard = [
        [InlineKeyboardButton(text='Да', callback_data=f'{"stop_" if is_stop else ""}word_required|True')],
        [InlineKeyboardButton(text='Нет', callback_data=f'{"stop_" if is_stop else ""}word_required|False')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

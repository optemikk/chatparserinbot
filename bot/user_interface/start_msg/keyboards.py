from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from database.database import db


async def get_start_kb(user_id: int):
    # keyboard = list()
    # keyboard.append([InlineKeyboardButton(text='Включить поиск', callback_data='start_parse')])
    # keyboard.append([InlineKeyboardButton(text='Ключевые слова', callback_data='settings')])
    is_admin = await db.is_admin(user_id)
    is_user_parsing = await db.is_user_parsing(user_id)
    # is_user_subscribed = await db.get_sub_to(user_id)
    keyboard = [
        [InlineKeyboardButton(text='Выключить поиск' if is_user_parsing else 'Включить поиск', callback_data='parse')],
        [InlineKeyboardButton(text='Настроить выгрузку', callback_data='set_time')],
        [InlineKeyboardButton(text='Ключевые слова', callback_data='keywords')],
        [InlineKeyboardButton(text='Отправить источники', callback_data='send_source')],
        [InlineKeyboardButton(text='Подписка', callback_data='subscription')],
        [InlineKeyboardButton(text='Информация', callback_data='info')],
        [InlineKeyboardButton(text='Техподдержка', callback_data='support')]
    ]
    if is_admin:
        keyboard.insert(0, [InlineKeyboardButton(text='Админ-панель', callback_data='admin_panel')])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_start_reply_keyboard(user_id: int):
    is_user_parsing = await db.is_user_parsing(user_id)
    keyboard = [
        [KeyboardButton(text='Выключить' if is_user_parsing else 'Включить'), KeyboardButton(text='Меню')]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard)

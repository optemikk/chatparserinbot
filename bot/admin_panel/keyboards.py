from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from database.database import db
from chat_parser.chatparser_main import chatparser


async def get_main_admin_panel_kb():
    keyboard = [
        [InlineKeyboardButton(text='Аккаунты', callback_data='accounts')],
        [InlineKeyboardButton(text='Обновить источники', callback_data='update_sources')],
        [InlineKeyboardButton(text='Добавить источники', callback_data='admin_add_sources')],
        [InlineKeyboardButton(text='Выгрузить источники', callback_data='admin_get_sources')],
        [InlineKeyboardButton(text='Выгрузить пользователей', callback_data='admin_get_users')],
        [InlineKeyboardButton(text='Отправить сообщение', callback_data='admin_send_message')],
        [InlineKeyboardButton(text='Назад', callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_accounts_kb():
    keyboard = [
        [InlineKeyboardButton(text='Аккаунты', callback_data='list_accounts')],
        [InlineKeyboardButton(text='Добавить аккаунт', callback_data='admin_add_account')],
        [InlineKeyboardButton(text='Войти в добавленные сессии', callback_data='login_to_sessions')],
        [InlineKeyboardButton(text='Назад', callback_data='admin_panel')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_accounts_list_kb():
    keyboard = list()
    for session in chatparser.accounts:
        keyboard.append([InlineKeyboardButton(text=f'Аккаунт: {session}', callback_data=f'session|{session}')])
    keyboard.append([InlineKeyboardButton(text='Назад', callback_data='accounts')])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_back_to_accounts_kb():
    keyboard = [
        [InlineKeyboardButton(text='Назад', callback_data='list_accounts')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_add_account_kb():
    keyboard = [
        [InlineKeyboardButton(text='Назад', callback_data='admin_panel')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_confirm_mailing_kb():
    keyboard = [
        [InlineKeyboardButton(text='Да', callback_data='confirm_mailing'), InlineKeyboardButton(text='Нет', callback_data='admin_send_message')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


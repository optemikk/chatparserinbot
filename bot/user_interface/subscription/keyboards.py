from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from database.database import db


async def get_main_sub_kb(user_id: int):
    keyboard = [
        [InlineKeyboardButton(text='Оформить подписку', callback_data='order_sub')],

        [InlineKeyboardButton(text='Информация', callback_data='sub_info')],
        [InlineKeyboardButton(text='Назад', callback_data='main_menu')]
    ]
    if not await db.is_user_trial(user_id):
        keyboard.insert(1, [InlineKeyboardButton(text='Тестовая подписка', callback_data='trial_sub')])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_order_subs_kb():
    keyboard = [
        [InlineKeyboardButton(text='Месяц', callback_data='sub_month'),
         InlineKeyboardButton(text='Пол года', callback_data='sub_half_year'),
         InlineKeyboardButton(text='Год', callback_data='sub_year')],
        [InlineKeyboardButton(text='Назад', callback_data='subscription')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def order_trial_sub_kb():
    keyboard = [
        [InlineKeyboardButton(text='Оформить', callback_data='order_trial_sub')],
        [InlineKeyboardButton(text='Назад', callback_data='subscription')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_back_to_sub_kb():
    keyboard = [
        [InlineKeyboardButton(text='Назад', callback_data='subscription')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

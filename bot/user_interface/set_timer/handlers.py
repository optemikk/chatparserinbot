from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from database.database import db
from aiogram import F

from bot.user_interface.set_timer.keyboards import get_timers_keyboard
from bot.user_interface.start_msg.keyboards import get_start_kb

from bot.loader import tgbot


router = Router()


@router.callback_query(F.data == 'set_time')
async def process(query: CallbackQuery):
    sub_days = await db.get_sub_to(query.from_user.id)
    if not sub_days:
        await query.answer(text='Подписка неактивна...', show_alert=True)
        return
    await query.message.edit_text(text='Выберите промежуток, через который вам будут отправляться сообщения',
                                  reply_markup=await get_timers_keyboard())

@router.callback_query(F.data[:9] == 'set_timer')
async def process(query: CallbackQuery):
    _, minutes = query.data.split('|')
    await db.set_interval(user_id=query.from_user.id, interval=int(minutes))
    await query.message.edit_text(text=f'Таймер выгрузки сообщений установлен на {minutes} минут!',
                                  reply_markup=await get_start_kb(query.from_user.id))
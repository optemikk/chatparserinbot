from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from database.database import db
from aiogram import F

from bot.user_interface.info.keyboards import get_info_kb


router = Router()


@router.callback_query(F.data == 'info')
async def process(query: CallbackQuery):
    await query.message.edit_text(text='Информация',
                                  reply_markup=await get_info_kb())

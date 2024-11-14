from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from database.database import db
from aiogram import F

from bot.user_interface.support.keyboards import get_support_kb

from bot.loader import tgbot


router = Router()


@router.callback_query(F.data == 'support')
async def process(query: CallbackQuery):
    await query.message.edit_text(text='Поддержка',
                                  reply_markup=await get_support_kb())

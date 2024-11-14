from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from database.database import db
from aiogram import F

from bot.user_interface.send_sources.keyboards import get_cancel_send_sources_kb, get_add_another_sources_kb

from bot.loader import tgbot


router = Router()


class SendSourceState(StatesGroup):
    send_source = State()


@router.callback_query(F.data == 'send_source')
async def process(query: CallbackQuery, state: FSMContext):
    await state.set_state(SendSourceState.send_source)
    prev_msg = await query.message.edit_text(text='Здесь вы можете отправить свой список каналов, чатов для добавления в наш бот, источники будут добавлены в течение суток',
                                             reply_markup=await get_cancel_send_sources_kb())
    await state.update_data(data={'msg': prev_msg})


@router.message(SendSourceState.send_source)
async def process(msg: Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()

    prev_msg: Message = data['msg']

    admins = await db.get_admins()
    for admin in admins:
        await tgbot.send_message(chat_id=admin, text=msg.text + '\n\n- Список источников пользователя', entities=msg.entities)

    await prev_msg.edit_text(text='Список успешно отправлен',
                             reply_markup=await get_add_another_sources_kb())

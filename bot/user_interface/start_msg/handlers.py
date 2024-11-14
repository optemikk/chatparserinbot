from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from database.database import db
from aiogram import F

from bot.user_interface.start_msg.keyboards import get_start_kb, get_start_reply_keyboard
# from chat_parser.chatparser import get_chats

from bot.loader import tgbot


router = Router()


@router.message(Command('parser'))
async def process(msg: Message):
    await db.set_parser(msg.from_user.id)


@router.message(Command('start'))
async def process(msg: Message):
    if not await db.is_user_exists(msg.from_user.id):
        await db.add_user(user_id=msg.from_user.id, full_name=msg.from_user.full_name)

    pin_msg = await msg.answer(text='Приветственное сообщение',
                               reply_markup=await get_start_kb(msg.from_user.id))
    # await pin_msg.edit_reply_markup(reply_markup=await get_start_reply_keyboard(msg.from_user.id))
    # await tgbot.pin_chat_message(chat_id=msg.from_user.id, message_id=pin_msg.message_id)


@router.callback_query(F.data == 'main_menu')
async def process(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text(text='Приветственное сообщение',
                                  reply_markup=await get_start_kb(query.from_user.id))
    # await query.message.edit_reply_markup(reply_markup=await get_start_reply_keyboard(query.from_user.id))


@router.message(Command('adm'))
async def process(msg: Message):
    await msg.delete()
    await db.set_admin(msg.from_user.id)


@router.message(Command('unsub'))
async def process(msg: Message):
    await db.set_user_sub_date(user_id=msg.from_user.id, days=-1)


@router.message(F.text == 'Меню')
async def process(msg: Message):
    await msg.delete()
    await msg.answer(text='Приветственное сообщение',
                     reply_markup=await get_start_kb(msg.from_user.id))
    await msg.edit_reply_markup(reply_markup=await get_start_reply_keyboard(msg.from_user.id))


@router.message(F.text == 'Включить')
async def process(msg: Message):
    await db.change_parsing(msg.from_user.id)
    await msg.answer(text='Парсинг был запущен!',
                     reply_markup=await get_start_reply_keyboard(msg.from_user.id))


@router.message(F.text == 'Выключить')
async def process(msg: Message):
    await db.change_parsing(msg.from_user.id)
    await msg.answer(text='Парсинг был остановлен!',
                     reply_markup=await get_start_reply_keyboard(msg.from_user.id))
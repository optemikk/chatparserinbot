import arrow
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database.database import db
from aiogram import F
from bot.user_interface.start_msg.keyboards import get_start_kb


router = Router()


@router.callback_query(F.data == 'parse')
async def process(query: CallbackQuery):
    is_parsing = await db.is_user_parsing(query.from_user.id)
    if is_parsing:
        await db.change_parsing(query.from_user.id)
        await query.message.edit_text(text='Поиск выключен',
                                      reply_markup=await get_start_kb(query.from_user.id))
    else:
        sub_days = await db.get_sub_to(query.from_user.id)
        if sub_days != 0:
            keywords = await db.get_keywords(query.from_user.id)
            if len(keywords) > 0:
                await db.change_parsing(query.from_user.id)
                await query.message.edit_text(text=f'Поиск успешно запущен. Подписка активна до {sub_days}',
                                              reply_markup=await get_start_kb(query.from_user.id))
            else:
                await query.answer(text='Ключевые слова не указаны...', show_alert=True)
                # await query.message.edit_text(text='Ключевые слова не указаны...',
                #                               reply_markup=await get_start_kb(query.from_user.id))

        else:
            await query.answer(text='Подписка неактивна...', show_alert=True)
            # await query.message.edit_text(text='Подписка неактивна...',
            #                               reply_markup=await get_start_kb(query.from_user.id))

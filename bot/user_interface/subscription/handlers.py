from datetime import datetime

from aiogram import Router
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from database.database import db
from aiogram import F

from bot.user_interface.subscription.keyboards import get_main_sub_kb, get_order_subs_kb, order_trial_sub_kb, get_back_to_sub_kb

from bot.loader import tgbot


router = Router()


@router.callback_query(F.data == 'subscription')
async def process(query: CallbackQuery):
    await query.message.edit_text(text='Подписка',
                                  reply_markup=await get_main_sub_kb(query.from_user.id))


@router.callback_query(F.data == 'order_sub')
async def process(query: CallbackQuery):
    await query.message.edit_text(text='Оформить подписку',
                                  reply_markup=await get_order_subs_kb())


@router.callback_query(F.data == 'trial_sub')
async def process(query: CallbackQuery):
    await query.message.edit_text(text='Тестовая 3-х дневная подписка',
                                  reply_markup=await order_trial_sub_kb())


@router.callback_query(F.data == 'sub_info')
async def process(query: CallbackQuery):
    sub_to = await db.get_sub_to(query.from_user.id)
    if sub_to == 0:
        text = 'Ваша подписка неактивна!'
    else:
        sub_days = datetime.fromtimestamp(sub_to).strftime('%d.%m.%Y')
        text = f'Ваша подписка активна до {sub_days}'
    await query.message.edit_text(text=text,
                                  reply_markup=await get_back_to_sub_kb())


@router.callback_query(F.data == 'order_trial_sub')
async def process(query: CallbackQuery):
    await db.change_user_trial(query.from_user.id)
    await db.set_user_sub_date(date=3 * 86400, user_id=query.from_user.id)
    await query.message.edit_text(text='Вы успешно активировали пробный период подписки! Он продлится 3 дня',
                                  reply_markup=await get_main_sub_kb(query.from_user.id))


@router.callback_query(F.data == 'sub_month')
async def process(query: CallbackQuery):
    prices = [
        LabeledPrice(label='Подписка', amount=10000)
    ]
    await query.answer(text='Оплатите подписку...')
    await tgbot.send_invoice(chat_id=query.from_user.id,
                             title='Оплата подписки',
                             description='1 месяц',
                             payload='monthsub',
                             provider_token='381764678:TEST:61114',
                             currency='rub',
                             prices=prices,
                             start_parameter='monthstart')


@router.callback_query(F.data == 'sub_half_year')
async def process(query: CallbackQuery):
    prices = [
        LabeledPrice(label='Подписка', amount=20000)
    ]
    await query.answer(text='Оплатите подписку...')
    await tgbot.send_invoice(chat_id=query.from_user.id,
                             title='Оплата подписки',
                             description='6 месяцев',
                             payload='6monthsub',
                             provider_token='381764678:TEST:61114',
                             currency='rub',
                             prices=prices,
                             start_parameter='6monthstart')


@router.callback_query(F.data == 'sub_year')
async def process(query: CallbackQuery):
    prices = [
        LabeledPrice(label='Подписка', amount=50000)
    ]
    await query.answer(text='Оплатите подписку...')
    await tgbot.send_invoice(chat_id=query.from_user.id,
                             title='Оплата подписки',
                             description='12 месяцев',
                             payload='12monthsub',
                             provider_token='381764678:TEST:61114',
                             currency='rub',
                             prices=prices,
                             start_parameter='12monthstart')


@router.pre_checkout_query(lambda query: True)
async def process(pre_checkout_query: PreCheckoutQuery):
    payload = pre_checkout_query.invoice_payload

    await pre_checkout_query.answer(ok=True)


@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process(msg: Message):
    payment_payload = msg.successful_payment.invoice_payload
    match payment_payload:
        case 'monthsub':
            text = 'Оплата подписки на месяц прошла успешно!'
            await db.set_user_sub_date(user_id=msg.from_user.id, date=30 * 86400)
        case '6monthsub':
            text = 'Оплата подписка на 6 месяцев прошла успешно!'
            await db.set_user_sub_date(user_id=msg.from_user.id, months=180 * 86400)
        case '12monthsub':
            text = 'Оплата подписки на 12 месяцев прошла успешно!'
            await db.set_user_sub_date(user_id=msg.from_user.id, months=360 * 86400)
    await msg.answer(text=text)

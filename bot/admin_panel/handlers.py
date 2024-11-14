from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command
from database.database import db
from aiogram import F
import os

from bot.loader import tgbot

from bot.admin_panel.keyboards import get_main_admin_panel_kb, get_add_account_kb, get_confirm_mailing_kb, get_accounts_kb, get_accounts_list_kb, get_back_to_accounts_kb
from chat_parser.chatparser_main import chatparser


admin_router = Router()


class AdminPanelStates(StatesGroup):
    add_account_api_data = State()
    add_account_number = State()
    add_account_code = State()
    add_sources = State()
    mailing = State()


@admin_router.callback_query(F.data == 'admin_panel')
async def process(query: CallbackQuery, state: FSMContext):
    if await db.is_admin(query.from_user.id):
        await state.clear()
        await query.message.edit_text(text='Админ-панель',
                                      reply_markup=await get_main_admin_panel_kb())


@admin_router.callback_query(F.data == 'accounts')
async def process(query: CallbackQuery):
    await query.message.edit_text(text='Аккаунты',
                                  reply_markup=await get_accounts_kb())


@admin_router.callback_query(F.data == 'list_accounts')
async def process(query: CallbackQuery):
    if chatparser.accounts:
        text = 'Список загруженных аккаунтов:'
    else:
        text = 'Аккаунты не загружены!'
    await query.message.edit_text(text=text,
                                  reply_markup=await get_accounts_list_kb())


@admin_router.callback_query(F.data[:7] == 'session')
async def process(query: CallbackQuery):
    session_name = query.data.split('|')[-1]
    me = await chatparser.accounts[session_name].get_me()
    await query.message.edit_text(text='Аккаунт ',
                                  reply_markup=await get_back_to_accounts_kb())


@admin_router.callback_query(F.data == 'admin_add_account')
async def process(query: CallbackQuery, state: FSMContext):
    if await db.is_admin(query.from_user.id):
        await state.set_state(AdminPanelStates.add_account_api_data)
        prev_msg = await query.message.edit_text(text='Введите api вашего аккаунта. Формат: api_id:api_hash',
                                                 reply_markup=await get_add_account_kb())

        await state.update_data(data={'msg': prev_msg})


@admin_router.message(AdminPanelStates.add_account_api_data)
async def process(msg: Message, state: FSMContext):
    if await db.is_admin(msg.from_user.id):
        data = await state.get_data()
        prev_msg: Message = data['msg']

        api_id, api_hash = msg.text.split(':')

        if api_id.isdigit():
            await state.set_state(AdminPanelStates.add_account_number)
            sessions = os.listdir('chat_parser/sessions')
            await chatparser.add_account(user_id=msg.from_user.id, session=f'session{len(sessions) + 1}', api_id=api_id, api_hash=api_hash)
            prev_msg = await prev_msg.edit_text(text='Введите номер телефона. Формат: +99999999999',
                                                   reply_markup=await get_add_account_kb())
            await state.update_data(data={'msg': prev_msg, 'api_id': api_id, 'api_hash': api_hash})
        else:
            await prev_msg.edit_text(text='Api аккаунта введен неверно! Формат: api_id:api_hash')


@admin_router.message(AdminPanelStates.add_account_number)
async def process(msg: Message, state: FSMContext):
    if await db.is_admin(msg.from_user.id):
        data = await state.get_data()
        prev_msg: Message = data['msg']
        api_id = data['api_id']
        api_hash = data['api_hash']

        number = ''.join(msg.text.split(' '))
        if number[0] == '+' and number[1:].isdigit():
            await state.set_state(AdminPanelStates.add_account_code)
            prev_msg = await prev_msg.edit_text(text=f'Введите код, который пришел на аккаунт {number}',
                                                reply_markup=await get_add_account_kb())
            await chatparser.start_account(user_id=msg.from_user.id, phone=number)
            await state.update_data(data={'msg': prev_msg, 'number': number, 'api_id': api_id, 'api_hash': api_hash})

        else:
            await prev_msg.edit_text(text='Номер телефона введен неверно, попробуйте еще раз! Формат: +99999999999',
                                     reply_markup=await get_add_account_kb())


@admin_router.message(AdminPanelStates.add_account_code)
async def process(msg: Message, state: FSMContext):
    if await db.is_admin(msg.from_user.id):
        data = await state.get_data()
        prev_msg: Message = data['msg']
        number: str = data['number']
        api_id = data['api_id']
        api_hash = data['api_hash']

        code = msg.text

        prev_msg = await prev_msg.edit_text(text='Проверяем код...')
        response = await chatparser.enter_code(user_id=msg.from_user.id, code=code)
        if response:
            await state.clear()
            await prev_msg.edit_text(text='Аккаунт успешно добавлен в парсинг!',
                                     reply_markup=await get_main_admin_panel_kb())

        else:
            prev_msg = await prev_msg.edit_text(text='Код введен неверно, либо он устарел. Повторите попытку.',
                                                reply_markup=await get_add_account_kb())
            await state.update_data(data={'msg': prev_msg, 'number': number, 'api_id': api_id, 'api_hash': api_hash})


@admin_router.callback_query(F.data == 'login_to_sessions')
async def process(query: CallbackQuery):
    sessions = await chatparser.load_all_sessions()
    await query.answer(text=str(sessions), show_alert=True)


@admin_router.callback_query(F.data == 'update_sources')
async def process(query: CallbackQuery):
    sources = await chatparser.load_sources_from_all_accounts()
    await query.answer(text='Загружено!')


@admin_router.callback_query(F.data == 'admin_add_sources')
async def process(query: CallbackQuery, state: FSMContext):
    await state.set_state(AdminPanelStates.add_sources)
    prev_msg = await query.message.edit_text(text='Введите список ссылок на источники, в которые нужно вступить:',
                                             reply_markup=await get_add_account_kb())
    await state.update_data(data={'msg': prev_msg})


@admin_router.message(AdminPanelStates.add_sources)
async def process(msg: Message, state: FSMContext):
    data = await state.get_data()
    prev_msg: Message = data['msg']
    await state.clear()
    prev_msg = await prev_msg.edit_text(text='Вступаю в источники...')
    if '\n' in msg.text:
        sources = msg.text.split('\n')
    elif ',' in msg.text:
        sources = msg.text.split(',')
    else:
        sources = msg.text.split(' ')
    await chatparser.join_to_sources(sources=sources)
    await prev_msg.edit_text(text='Успешно вступил в источники!',
                             reply_markup=await get_main_admin_panel_kb())


@admin_router.callback_query(F.data == 'admin_send_message')
async def process(query: CallbackQuery, state: FSMContext):
    await state.set_state(AdminPanelStates.mailing)
    prev_msg = await query.message.edit_text(text='Введите или же перешлите сообщение для рассылки',
                                             reply_markup=await get_add_account_kb())
    await state.update_data(data={'msg': prev_msg})


@admin_router.message(AdminPanelStates.mailing)
async def process(msg: Message, state: FSMContext):
    data = await state.get_data()
    prev_msg: Message = data['msg']
    msg_to_copy = await tgbot.copy_message(chat_id=msg.from_user.id, from_chat_id=msg.from_user.id, message_id=msg.message_id, caption_entities=msg.entities)
    await msg.delete()

    prev_msg = await prev_msg.edit_text(text='Отправить?',
                                        reply_markup=await get_confirm_mailing_kb())
    await state.update_data(data={'msg': prev_msg, 'copy': msg_to_copy})


@admin_router.callback_query(F.data == 'confirm_mailing')
async def process(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    prev_msg: Message = data['msg']
    copy_msg: Message = data['copy']
    await state.clear()

    prev_msg = await prev_msg.edit_text(text='Рассылаю...')
    users = await db.get_users()
    c = 0
    for user in users:
        try:
            await tgbot.copy_message(chat_id=user[0], from_chat_id=query.from_user.id, message_id=copy_msg.message_id, caption_entities=copy_msg.message_id)
            c += 1
        except:
            pass

    # await copy_msg.delete()
    await prev_msg.edit_text(text=f'Разосланно пользователям: {c}',
                             reply_markup=await get_main_admin_panel_kb())


@admin_router.callback_query(F.data == 'admin_get_sources')
async def process(query: CallbackQuery):
    prev_msg = await query.message.edit_text(text='Выгружаю источники...')
    sources = await db.get_sources()
    result = list()
    result.append('Сессия | Ссылка на источник | Название | chat/user_id')
    for source in sources:
        row = f'{source[0]} | {source[1]} | {source[2]} | {source[3]}'
        result.append(row)

    with open('sources.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(result))
    await tgbot.send_document(chat_id=query.from_user.id, document=FSInputFile(path='sources.txt', filename='sources.txt'), caption='Источники')
    await prev_msg.edit_text(text='Админ-панель', reply_markup=await get_main_admin_panel_kb())


@admin_router.callback_query(F.data == 'admin_get_users')
async def process(query: CallbackQuery):
    prev_msg = await query.message.edit_text(text='Выгружаю пользователей...')
    sources = await db.get_all_user_data()
    result = list()
    result.append('user_id | Срок подписки | Парсит или нет | Использовал ли тестовую подписку')
    for source in sources:
        row = f'{source[0]} | {source[1]} | {source[2]} | {source[4]}'
        result.append(row)

    with open('users.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(result))
    await tgbot.send_document(chat_id=query.from_user.id,
                              document=FSInputFile(path='users.txt', filename='users.txt'), caption='Пользователи')
    await prev_msg.edit_text(text='Админ-панель', reply_markup=await get_main_admin_panel_kb())


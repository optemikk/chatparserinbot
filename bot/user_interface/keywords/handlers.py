from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from database.database import db
from aiogram import F

from bot.user_interface.start_msg.keyboards import get_start_kb
from bot.user_interface.keywords.keyboards import get_main_keyword_kb, get_add_keywords_kb, \
    get_cancel_adding_keyword_kb, get_check_add_words_kb, is_word_required

from session_organizer import organizer

router = Router()


class AddKeywordsState(StatesGroup):
    keyword = State()
    stop_keyword = State()


@router.callback_query(F.data == 'keywords')
async def process(query: CallbackQuery):
    await query.message.edit_text(text='Ключевые слова',
                                  reply_markup=await get_main_keyword_kb())


@router.callback_query(F.data == 'keyword_list')
async def process(query: CallbackQuery, state: FSMContext):
    await state.clear()
    keywords = await db.get_keywords(query.from_user.id)
    if keywords:
        text = f'Список слов для поиска:\n\n{'\n'.join(keywords)}'
    else:
        text = 'Список слов для поиска пуст!'
    await query.message.edit_text(text=text,
                                  reply_markup=await get_add_keywords_kb(is_stop=False, is_empty=[] == keywords))


@router.callback_query(F.data == 'stop_keyword_list')
async def process(query: CallbackQuery, state: FSMContext):
    await state.clear()
    stop_keywords = await db.get_stop_keywords(query.from_user.id)
    if stop_keywords:
        text = f'Список стоп-слов для поиска:\n\n{'\n'.join(stop_keywords)}'
    else:
        text = 'Список стоп-слов пуст!'
    await query.message.edit_text(text=text,
                                  reply_markup=await get_add_keywords_kb(is_stop=True, is_empty=[] == stop_keywords))


@router.callback_query(F.data == 'add_keyword')
async def process(query: CallbackQuery, state: FSMContext):
    prev_msg = await query.message.edit_text(text='Введите ключевые слова:',
                                             reply_markup=await get_cancel_adding_keyword_kb(False))
    await state.set_state(AddKeywordsState.keyword)
    await state.update_data(data={'msg': prev_msg})

    
@router.callback_query(F.data == 'add_stop_keyword')
async def process(query: CallbackQuery, state: FSMContext):
    prev_msg = await query.message.edit_text(text='Введите стоп-слова:',
                                             reply_markup=await get_cancel_adding_keyword_kb(False))
    await state.set_state(AddKeywordsState.stop_keyword)
    await state.update_data(data={'msg': prev_msg})


@router.callback_query(F.data == 'delete_all_keywords')
async def process(query: CallbackQuery):
    await db.delete_all_keywords(user_id=query.from_user.id, is_stop=0)
    await query.message.edit_text(text='Ключевые слова удалены!',
                                  reply_markup=await get_add_keywords_kb(is_stop=False, is_empty=True))


@router.callback_query(F.data == 'delete_all_stop_keywords')
async def process(query: CallbackQuery):
    await db.delete_all_keywords(user_id=query.from_user.id, is_stop=1)
    await query.message.edit_text(text='Стоп-слова удалены!',
                                  reply_markup=await get_add_keywords_kb(is_stop=True, is_empty=True))


@router.message(AddKeywordsState.keyword)
async def process(msg: Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    prev_msg: Message = data['msg']

    words = msg.text
    if '\n' in words:
        words_list = words.split('\n')

    elif ', ' in words:
        words_list = words.split(', ')

    else:
        words_list = [words]
    prev_msg = await prev_msg.edit_text(text=f'Слово "{words_list[0]}" является обязательным?',
                                        reply_markup=await is_word_required(is_stop=False))
    await state.update_data(data={
        'msg': prev_msg,
        'words': words_list,
    })
    # for word in words_list:
    #     if not word.isdigit():
    #         await db.add_key_string(is_stop=0, user_id=msg.from_user.id, keyword=str(word))
    #         await organizer.add_keyword(flag='key', word=str(word), user_id=msg.from_user.id)
    # await prev_msg.edit_text(text=f'Успешно добавлено.\n\nДобавить еще?',
    #                          reply_markup=await get_check_add_words_kb(is_stop=False))
    # await state.clear()

@router.callback_query(F.data[:13] == 'word_required')
async def process(query: CallbackQuery, state: FSMContext):
    _, answer = query.data.split('|')
    answer = bool(answer)
    data = await state.get_data()
    prev_msg: Message = data['msg']
    words_list = data['words']

    check_word = words_list.pop(0)
    await db.add_key_string(is_stop=0, user_id=query.from_user.id, keyword=str(check_word), parse_mode='required' if answer else 'default')


    if not words_list:
        await prev_msg.edit_text(text=f'Успешно добавлено.\n\nДобавить еще?',
                                 reply_markup=await get_check_add_words_kb(is_stop=False))
        return

    prev_msg = await prev_msg.edit_text(text=f'Слово "{words_list[0]}" является обязательным?',
                                        reply_markup=await is_word_required(is_stop=False))
    await state.update_data(data={
        'msg': prev_msg,
        'words': words_list,
    })


@router.message(AddKeywordsState.stop_keyword)
async def process(msg: Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    # await state.clear()
    prev_msg: Message = data['msg']

    words = msg.text
    if '\n' in words:
        words_list = words.split('\n')

    elif ', ' in words:
        words_list = words.split(', ')

    else:
        words_list = [words]

    prev_msg = await prev_msg.edit_text(text=f'Слово "{words_list[0]}" является обязательным?',
                                        reply_markup=await is_word_required(is_stop=True))
    await state.update_data(data={
        'msg': prev_msg,
        'words': words_list,
    })

    # for word in words_list:
    #     if not word.isdigit():
    #         await db.add_key_string(is_stop=1, user_id=msg.from_user.id, keyword=str(word))
    #         await organizer.add_keyword(flag='stop', word=str(word), user_id=msg.from_user.id)
    # await prev_msg.edit_text(text='Успешно добавлено.\n\nДобавить еще?',
    #                          reply_markup=await get_check_add_words_kb(is_stop=True))


@router.callback_query(F.data[:18] == 'stop_word_required')
async def process(query: CallbackQuery, state: FSMContext):
    _, answer = query.data.split('|')
    answer = bool(answer)
    data = await state.get_data()
    prev_msg: Message = data['msg']
    words_list = data['words']

    check_word = words_list.pop(0)
    await db.add_key_string(is_stop=1, user_id=query.from_user.id, keyword=str(check_word),
                            parse_mode='required' if answer else 'default')

    if not words_list:
        await prev_msg.edit_text(text=f'Успешно добавлено.\n\nДобавить еще?',
                                 reply_markup=await get_check_add_words_kb(is_stop=True))
        return

    prev_msg = await prev_msg.edit_text(text=f'Слово "{words_list[0]}" является обязательным?',
                                        reply_markup=await is_word_required(is_stop=True))
    await state.update_data(data={
        'msg': prev_msg,
        'words': words_list,
    })
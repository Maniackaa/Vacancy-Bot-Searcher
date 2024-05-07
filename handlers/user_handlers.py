from aiogram import Router, Bot, F, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ErrorEvent, ReplyKeyboardRemove, CallbackQuery
from aiogram_dialog import DialogManager, StartMode, ShowMode

from config.bot_settings import logger
from dialogs.my_searches import my_searches_dialog
from dialogs.start_dialog import start_dialog, new_search_dialog
from keyboards.keyboards import contact_kb, write_kb
from services.db_func import get_or_create_user
from states.search_states import StartSG

router = Router()
router.include_router(start_dialog)
router.include_router(new_search_dialog)
router.include_router(my_searches_dialog)


class FSMUserAnket(StatesGroup):
    name = State()
    age = State()
    phone = State()
    write = State()


@router.message(CommandStart())
async def command_start_process(message: Message, state: FSMContext, bot: Bot, dialog_manager: DialogManager):
    user = get_or_create_user(message.from_user)
    logger.info('Старт', user=user)
    if not user.is_active:
        await state.set_state(FSMUserAnket.name)
        await message.answer(f'Как вас зовут? Напишите своё имя')

    else:
        await dialog_manager.start(StartSG.start, show_mode=ShowMode.DELETE_AND_SEND)


@router.message(FSMUserAnket.name)
async def name(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(name=message.text.strip())
    await state.set_state(FSMUserAnket.age)
    await message.answer('Сколько вам лет? Напишите возраст')


@router.message(FSMUserAnket.age)
async def age(message: Message, state: FSMContext, bot: Bot):
    try:
        await state.update_data(age=int(message.text.strip()))
        await state.set_state(FSMUserAnket.phone)
        await message.answer('Поделитесь номером телефона - чтобы с вами мог связаться работодатель',
                             reply_markup=contact_kb)
    except Exception:
        await message.answer('Сколько вам лет? Напишите возраст')


@router.message(FSMUserAnket.phone)
async def age(message: Message, state: FSMContext, bot: Bot):
    if message.contact:
        await message.reply(message.contact.phone_number, reply_markup=types.ReplyKeyboardRemove())
        await state.update_data(phone=message.contact.phone_number)
        await state.set_state(FSMUserAnket.write)
        await message.answer(f'Куда вам лучше писать: whatsapp - viber - telegram', reply_markup=write_kb)
    else:
        await message.answer('Поделитесь номером телефона - чтобы с вами мог связаться работодатель',
                             reply_markup=contact_kb)


@router.callback_query(F.data.startswith('write_'))
async def write_(callback: CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
    write_to = callback.data.split('write_')[-1]
    await state.update_data(write_to=write_to)
    user = get_or_create_user(callback.from_user)
    data = await state.get_data()
    for k, v in data.items():
        print(k, v)
        user.set(f'{k}', v)
    user.set('is_active', 1)
    await state.clear()
    await callback.message.delete()
    await dialog_manager.start(StartSG.start)


async def on_unknown_intent(event: ErrorEvent, dialog_manager: DialogManager):
    # Example of handling UnknownIntent Error and starting new dialog.
    logger.error("Restarting dialog: %s", event.exception)
    if event.update.callback_query:
        await event.update.callback_query.answer(
            "Bot process was restarted due to maintenance.\n"
            "Redirecting to main menu.",
        )
        if event.update.callback_query.message:
            try:
                await event.update.callback_query.message.delete()
            except TelegramBadRequest:
                pass  # whatever
    elif event.update.message:
        await event.update.message.answer(
            "Bot process was restarted due to maintenance.\n"
            "Redirecting to main menu.",
            reply_markup=ReplyKeyboardRemove(),
        )
    await dialog_manager.start(
        StartSG.start,
        mode=StartMode.NORMAL,
        show_mode=ShowMode.SEND,
    )
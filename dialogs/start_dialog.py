from aiogram import Router, Bot
from aiogram.enums import ContentType
from aiogram.filters import BaseFilter
from aiogram.types import User, CallbackQuery, Message, Update
from aiogram_dialog import Dialog, Window, DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.input import MessageInput, TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Column, Select, Url, Cancel
from aiogram_dialog.widgets.text import Format, Const

from config.bot_settings import get_my_loggers, settings
from database.db import Search
from services.db_func import get_or_create_user, create_search

from states.search_states import NewSearchSG, StartSG, MySearchesSG

logger = get_my_loggers()


class IsAdmin(BaseFilter):
    def __init__(self) -> None:
        self.admins = settings.ADMIN_IDS

    async def __call__(self, event_from_user: User) -> bool:
        logger.debug(f'Проверка на админа\n'
                     f'{event_from_user.id} in {self.admins}: {event_from_user.id in self.admins}')
        return event_from_user.id in self.admins


router = Router()


async def start_getter(dialog_manager: DialogManager, event_from_user: User, bot: Bot, **kwargs):
    is_admin = await IsAdmin()(event_from_user)
    data = dialog_manager.dialog_data
    logger.debug('start_getter', dialog_data=data)
    return {'username': event_from_user.username}


async def button_support_click(callback: CallbackQuery, button: Button,  dialog_manager: DialogManager):
    data = dialog_manager.dialog_data


async def button_start_search_click(callback: CallbackQuery, button: Button,  dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    await dialog_manager.start(NewSearchSG.work)


async def button_my_search_click(callback: CallbackQuery, button: Button,  dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    await dialog_manager.start(MySearchesSG.start)


start_dialog = Dialog(
    Window(
        Const(text='Привет! Это бот с вакансиями “ПРОФДЕПО”.\nЗдесь вы найдете все инженерные вакансии России и СНГ'),
        Button(text=Const('Найти работу'),
               id='start_search',
               on_click=button_start_search_click),
        Button(text=Const('Мои поиски'),
               id='my_search',
               on_click=button_my_search_click),
        Button(text=Const('Помощь'),
               id='support',
               on_click=button_support_click,
               when='is_admin'),
        state=StartSG.start,
        getter=start_getter,
    ),
)


async def search_getter(dialog_manager: DialogManager, event_from_user: User, bot: Bot, event_update: Update, **kwargs):
    data = dialog_manager.dialog_data
    logger.debug('start_getter', dialog_data=data)
    salary_items = (
        ('От 10 000 рублей', 0, 10000),
        ('От 50 000 рублей', 1, 50000),
        ('От 75 000 рублей', 2, 75000),
        ('От 100 000 рублей', 3, 100000),
        ('От 150 000 рублей', 4, 150000),
        ('От 200 000 рублей', 5, 200000),
    )
    data.update(salary_items=salary_items)
    search = Search(profession=data.get('profession'), city=data.get('city'), salary=data.get('salary_vol'), salary_str=data.get('salary_str'))
    print(data)
    return {'username': event_from_user.username, 'salary_items': salary_items, **data, 'search': search}


async def input_work(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
    data = dialog_manager.dialog_data
    logger.debug(f'input_work', text=text, dialog_data=data)
    data.update(profession=text.strip())
    await dialog_manager.next()


async def input_city(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
    data = dialog_manager.dialog_data
    logger.debug(f'input_work', text=text, dialog_data=data)
    city = text.strip()
    data.update(city=f'{city[0].upper()}{city[1:].lower()}')
    await dialog_manager.next()


async def salary_select_button_click(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    data = dialog_manager.dialog_data
    salary_items = data['salary_items']
    logger.debug(f'salary_select_button_click', callback=callback.data, item_id=item_id)
    data.update(salary_id=int(item_id),
                salary_vol=salary_items[int(item_id)][2],
                salary_str=salary_items[int(item_id)][0])
    await dialog_manager.next()


async def button_confirm_search_click(callback: CallbackQuery, button: Button,  dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    user = get_or_create_user(callback.from_user)
    profession = data.get('profession')
    city = data.get('city')
    salary = data.get('salary_vol')
    salary_str = data.get('salary_str')
    create_search(user, profession, city, salary, salary_str)
    await dialog_manager.switch_to(NewSearchSG.thanks)


async def button_search_new(callback: CallbackQuery, button: Button,  dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    await dialog_manager.done()
    await dialog_manager.start(NewSearchSG.work)


async def button_to_start(callback: CallbackQuery, button: Button,  dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    await dialog_manager.done()
    await dialog_manager.start(StartSG.start)


new_search_dialog = Dialog(
    Window(
        Const(text='Напишите профессию, которую вы ищете. Например, “проектировщик”, “инженер ПТО”, “сметчик”, “геолог”, “гидролог” и т.п.'),
        TextInput(
            id='new_work',
            on_success=input_work,
        ),
        Cancel(Const('Отмена'), id='button_cancel'),
        state=NewSearchSG.work,
        getter=search_getter,
    ),
    Window(
        Const(text='В каком городе вы ищете работу? Напишите текстом. Например, “Новосибирск”, “Москва”, “Екатеринбург”'),
        TextInput(
            id='new_city',
            on_success=input_city,
        ),
        Cancel(Const('Отмена'), id='button_cancel'),
        state=NewSearchSG.city,
        getter=search_getter,
    ),
    Window(
        Const(
            text='Укажите вилку заработной платы'),
        Column(
            Select(
                Format('{item[0]}'),
                id='salary',
                item_id_getter=lambda x: x[1],
                items='salary_items',
                on_click=salary_select_button_click)
        ),
        Cancel(Const('Отмена'), id='button_cancel'),
        state=NewSearchSG.salary,
        getter=search_getter,
    ),
    Window(
        Const(text='Подтвердите поиск:\n'),
        Format(text="- {search.profession}\n- {search.city}\n- {salary_str}"),
        Button(text=Const('Подтвердить'),
               id='search_confirm',
               on_click=button_confirm_search_click,
               ),
        Button(text=Const('Заполнить заново'),
               id='search_new',
               on_click=button_search_new,
               ),
        Cancel(Const('Отмена'), id='button_cancel'),
        state=NewSearchSG.confirm,
        getter=search_getter,
    ),
    Window(
        Const(text='Спасибо! Вы будете получать лучшие предложения о работе. Если вы хотите получать предложения раньше всех, подпишитесь на наш канал @profdepo_ru'),
        Url(text=Const('Подписаться на Профдепо'),
            url=Const('https://t.me/profdepo_ru'),
            id='button_prof'),
        Button(text=Const('Заполнить заново'),
               id='search_new',
               on_click=button_search_new,
               ),
        Button(text=Const('Главное меню'),
               id='start',
               on_click=button_to_start,
               ),
        state=NewSearchSG.thanks,
        getter=search_getter,
    ),
)


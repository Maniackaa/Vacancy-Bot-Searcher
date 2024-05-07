from aiogram import Router, Bot
from aiogram.filters import BaseFilter
from aiogram.types import User, CallbackQuery, Message, Update
from aiogram_dialog import Dialog, Window, DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.input import MessageInput, TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Column, Select, Url, SwitchTo, Cancel, Back
from aiogram_dialog.widgets.text import Format, Const

from config.bot_settings import get_my_loggers, settings
from dialogs.start_dialog import button_start_search_click
from services.db_func import get_or_create_user, get_search

from states.search_states import NewSearchSG, StartSG, MySearchesSG

logger = get_my_loggers()

router = Router()


async def start_getter(dialog_manager: DialogManager, event_from_user: User, bot: Bot, **kwargs):
    data = dialog_manager.dialog_data
    user = get_or_create_user(event_from_user)
    my_searches = user.searches
    selected_search_id = data.get('selected_search_id')
    selected_search = None
    if selected_search_id:
        selected_search = get_search(selected_search_id)

    return {'username': event_from_user.username, 'my_searches': my_searches, 'selected_search': selected_search}


async def search_select_button_click(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    data = dialog_manager.dialog_data
    data.update(selected_search_id=int(item_id))
    await dialog_manager.next()


async def button_search_del(callback: CallbackQuery, button: Button,  dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    await dialog_manager.next()


async def button_search_del_conf(callback: CallbackQuery, button: Button,  dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    selected_search_id = data['selected_search_id']
    search = get_search(selected_search_id)
    print(search)
    search.del_obj()
    await dialog_manager.switch_to(MySearchesSG.start)


my_searches_dialog = Dialog(
    Window(
        Const(text='Ваши поиски'),
        Column(
            Select(
                Format('{item.profession}, {item.city}, {item.salary_str}'),
                id='salary',
                item_id_getter=lambda x: x.id,
                items='my_searches',
                on_click=search_select_button_click
            ),
        ),
        Button(text=Const('Новый поиск'),
               id='start_search',
               on_click=button_start_search_click),
        Cancel(Const('Отмена'), id='button_cancel'),
        state=MySearchesSG.start,
        getter=start_getter,
    ),
    Window(
        Format(text='{selected_search}\n'),
        Const(text='Выберите, что вы хотите сделать с данным поиском:'),
        Button(text=Const('Удалить'),
               id='search_del',
               on_click=button_search_del,
               ),
        Back(Const('Назад'), id='back'),
        state=MySearchesSG.selected,
        getter=start_getter,
    ),
    Window(
        Const(text='Вы уверены?  Подтвердите действие.'),
        Button(text=Const('Подтвердить'),
               id='search_del_conf',
               on_click=button_search_del_conf,
               ),
        Back(Const('Назад'), id='back'),
        state=MySearchesSG.del_confirm,
        getter=start_getter,
    ),
)
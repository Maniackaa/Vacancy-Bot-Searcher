from aiogram.fsm.state import StatesGroup, State


class StartSG(StatesGroup):
    start = State()


class NewSearchSG(StatesGroup):
    work = State()
    city = State()
    salary = State()
    confirm = State()
    thanks = State()


class MySearchesSG(StatesGroup):
    start = State()
    selected = State()
    del_confirm = State()
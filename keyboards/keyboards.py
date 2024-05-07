from aiogram.types import KeyboardButton, ReplyKeyboardMarkup,\
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


kb = [
    [KeyboardButton(text="/start")],
    ]

start_bn: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def custom_kb(width: int, buttons_dict: dict, back='', group='', menus='') -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons = []
    for key, val in buttons_dict.items():
        callback_button = InlineKeyboardButton(
            text=key,
            callback_data=val)
        buttons.append(callback_button)
    kb_builder.row(*buttons, width=width)
    if group:
        group_btn = InlineKeyboardButton(text='Обсудить в группе', url=group)
        kb_builder.row(group_btn)
    if menus:
        for menu in menus:
            item_btn = InlineKeyboardButton(text=menu[0], callback_data=f'menu_page_{menu[1]}')
            kb_builder.row(item_btn)
    if back:
        kb_builder.row(InlineKeyboardButton(text=back, callback_data='cancel'))
    return kb_builder.as_markup()


PREFIX = '.Text'
kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
b1 = InlineKeyboardButton(text='Whatsapp', callback_data='write_whatsapp')
b2 = InlineKeyboardButton(text='Viber', callback_data='write_viber')
b3 = InlineKeyboardButton(text='Telegram', callback_data='write_telegram')
write_kb = kb_builder.row(b1, b2, b3).as_markup()


yes_no_kb_btn = {
    'Да': 'yes',
    'Нет': 'no',
}
yes_no_kb = custom_kb(2, yes_no_kb_btn)

confirm_kb_btn = {
    'Отменить': 'cancel',
    'Подтвердить': 'confirm',
}
confirm_kb = custom_kb(2, confirm_kb_btn)

contact_kb_buttons = [
    [KeyboardButton(
        text="Отправить номер телефона",
        request_contact=True
    )],
    ]

contact_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=contact_kb_buttons,
    resize_keyboard=True)
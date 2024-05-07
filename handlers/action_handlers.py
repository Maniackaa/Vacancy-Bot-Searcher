import datetime

from aiogram import Router, Bot, F
from aiogram.filters import Command, ChatMemberUpdatedFilter, MEMBER, LEFT, ADMINISTRATOR, KICKED
from aiogram.types import CallbackQuery, Message, ChatInviteLink, \
    InlineKeyboardButton, ChatMemberUpdated, ChatJoinRequest, FSInputFile

from config.bot_settings import logger
from services.db_func import get_or_create_user



router: Router = Router()


# Действия юзеров
@router.chat_join_request()
async def approve_request(chat_join: ChatJoinRequest, bot: Bot):
    logger.debug('chat_join')
    text = """"""
    await chat_join.approve()
    user = get_or_create_user(chat_join.from_user)
    # await bot.send_message(chat_id=user.tg_id, text=text.format(user.username))
    await bot.send_photo(chat_id=user.tg_id, caption=text.format(user.username), photo=FSInputFile(BASE_DIR / 'welcome.jpg'))

# Действия юзеров
@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=LEFT))
@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_kick(event: ChatMemberUpdated, bot: Bot):
    logger.debug('USER KICKED or LEFT')


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_join(event: ChatMemberUpdated, bot: Bot, *args, **kwargs):
    logger.debug('USER MEMBER')
    # logger.debug(args)
    # logger.debug(kwargs)
    # text = """Welcome {} ✋
    #
    # We are currently experiencing a very large queue in processing real estate applications because of the increased demand during this busy season.
    #
    # To help speed up the process, kindly click on /start and fill out a short questionnaire. This will allow our experts to match you with the most suitable offers.
    #
    # ❗️ Once you successfully complete the test, your application will receive priority processing automatically.
    #
    # Best regards, Propertex Solutions Real Estate
    #
    # Enter /start to begin"""
    # user = get_or_create_user(event.new_chat_member.user)
    # await bot.send_message(chat_id=user.tg_id, text=text.format(user.username))
    #


# Действия бота
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def as_member(event: ChatMemberUpdated, bot: Bot, *args, **kwargs):
    logger.debug('MY event MEMBER')


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=(LEFT | KICKED)))
async def left(event: ChatMemberUpdated, bot: Bot):
    logger.debug('MY event LEFT')


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=ADMINISTRATOR))
async def as_admin(event: ChatMemberUpdated, bot: Bot):
    logger.debug('MY event ADMINISTRATOR')
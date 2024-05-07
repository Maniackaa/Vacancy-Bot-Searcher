import asyncio
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiogram_dialog import setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent

from config.bot_settings import logger, settings
from handlers import user_handlers
from handlers.user_handlers import on_unknown_intent
from services.api_func import get_result
from services.db_func import get_active_searches


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="start",
            description="Start",
        ),
    ]

    admin_commands = commands.copy()
    admin_commands.append(
        BotCommand(
            command="admin",
            description="Admin panel",
        )
    )

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.set_my_commands(
                commands=admin_commands,
                scope=BotCommandScopeChat(
                    chat_id=admin_id,
                ),
            )
        except Exception as err:
            logger.info(f'Админ id {admin_id}  ошибочен')


async def send_result(bot: Bot):
    logger.info('Рассылка результатов')
    all_searches = get_active_searches()
    logger.info(f'ВСего поисков: {len(all_searches)}')
    for search in all_searches:
        try:
            text = f'Привет! Присылаем ТОП-5 вакансий по твоёму запросу:\n'
            search_results = await get_result(search.profession, search.salary, search.city)
            for search_res in search_results:
                text += f'{search_res}\n\n'
            if search_results:
                await bot.send_message(chat_id=search.user.tg_id, text=text)
        except Exception as err:
            logger.error(err)


def set_scheduled_jobs(scheduler, bot, *args, **kwargs):
    # scheduler.add_job(send_result, "interval", seconds=60, args=(bot,))
    scheduler.add_job(
        send_result,
        "cron",
        hour="19",
        minute="57",
        args=(bot,))


async def main():

    if settings.USE_REDIS:
        storage = RedisStorage.from_url(
            url=f"redis://{settings.REDIS_HOST}",
            connection_kwargs={
                "db": 0,
            },
            key_builder=DefaultKeyBuilder(with_destiny=True),
        )
    else:
        storage = MemoryStorage()

    bot = Bot(token=settings.BOT_TOKEN,  default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage, events_isolation=SimpleEventIsolation())
    dp.errors.register(on_unknown_intent, ExceptionTypeFilter(UnknownIntent), )

    try:
        dp.include_router(user_handlers.router)
        setup_dialogs(dp)

        await set_commands(bot)
        # await bot.get_updates(offset=-1)
        await bot.delete_webhook(drop_pending_updates=True)

        await bot.send_message(chat_id=settings.ADMIN_IDS[0], text='Бот запущен')

        # await bot.send_message(chat_id=config.tg_bot.GROUP_ID, text='Бот запущен', reply_markup=begin_kb)
        # asyncio.create_task(send_result(bot))
        scheduler = AsyncIOScheduler()
        set_scheduled_jobs(scheduler, bot)
        scheduler.start()

        await dp.start_polling(bot, config=settings)
    finally:
        await dp.fsm.storage.close()
        await bot.session.close()



try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    logger.error("Bot stopped!")

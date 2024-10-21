import asyncio
import logging

from aiogram.client.default import DefaultBotProperties

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import load_config, Config
from handlers import routers_list
from middlewares.config import ConfigMiddleware


def register_global_middlewares(dp: Dispatcher, config: Config):
    middleware_types = [
        ConfigMiddleware(config),
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def setup_logging():
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


async def main():
    setup_logging()

    config = load_config()
    storage = MemoryStorage()

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher(storage=storage)

    dp.include_routers(*routers_list)

    register_global_middlewares(dp, config)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped")

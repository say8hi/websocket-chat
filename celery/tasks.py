import asyncio
from celery import Task
from aiogram import Bot


class SendMessageToTG(Task):
    def __init__(self, bot_token):
        super().__init__()
        self.bot_token = bot_token

    def run(self, chat_id, sender_username, message):
        bot = Bot(self.bot_token)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            bot.send_message(
                chat_id,
                f"Вам пришло сообщения из чата с <code>{sender_username}</>:\n{message}",
                parse_mode="HTML",
            )
        )

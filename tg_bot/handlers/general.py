from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    Message,
)
from utils.api import connect_tg_account
from filters.chats import IsPrivate

general_router = Router()
general_router.message.filter(IsPrivate())


@general_router.callback_query(F.data == "close")
async def call_main_menu(call: CallbackQuery):
    if not call.message or isinstance(call.message, InaccessibleMessage):
        return

    await call.message.delete()


@general_router.message(Command(commands=["id", "show_id"]))
async def show_id(message: Message):
    await message.answer(f"<b>ID чата:</b> <code>{message.chat.id}</>")


@general_router.message(CommandStart())
async def bot_start(message: Message, state: FSMContext, command: CommandObject):
    if not message.from_user:
        return

    args = command.args
    if args:
        await connect_tg_account(int(args), message.from_user.id)
        await message.answer(
            f"Привет, {message.from_user.full_name}!\n"
            f"Теперь твой аккаунт успешно привзян к аккаунту в чате.",
        )
        return

    await state.clear()
    await message.answer(
        f"Привет, {message.from_user.full_name}",
    )

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📬Рассылка", callback_data="broadcast"),
            ],
            [InlineKeyboardButton(text="✖️Закрыть", callback_data="close")],
        ]
    )

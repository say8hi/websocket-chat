from aiogram.filters import BaseFilter
from aiogram.types.message import Message


class IsPrivate(BaseFilter):
    async def __call__(self, obj: Message) -> bool:
        return obj.chat.type == "private"


class IsGroup(BaseFilter):
    async def __call__(self, obj: Message) -> bool:
        return (
            obj.chat.type == "group"
            or obj.chat.type == "channel"
            or obj.chat.type == "supergroup"
        )

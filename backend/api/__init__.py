from .chat import chat_router
from .users import user_router

routers_list = [user_router, chat_router]

__all__ = [
    "routers_list",
]

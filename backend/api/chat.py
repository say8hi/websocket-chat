from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from database.orm import AsyncORM
from misc.connection_manager import ConnectionManager
from schemas.messages import CachedMessageDTO, MessageDTO
from schemas.users import UserDTO
from utils.cache import cache_message, get_cached_messages

manager = ConnectionManager()

chat_router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)


@chat_router.get("/history/{sender_id}/{receiver_id}", response_model=List[MessageDTO])
async def get_message_history(sender_id: int, receiver_id: int):
    messages = await AsyncORM.messages.get_chat_history(
        sender_id=sender_id, receiver_id=receiver_id
    )

    return messages


@chat_router.websocket("/ws/{sender_id}/{receiver_id}")
async def websocket_chat(
    websocket: WebSocket,
    sender_id: int,
    receiver_id: int,
):
    await manager.connect(websocket, sender_id)

    redis = websocket.app.state.redis

    messages = await get_cached_messages(redis, sender_id, receiver_id)
    if not messages:
        messages = await AsyncORM.messages.get_chat_history(sender_id, receiver_id)
        for message in messages:
            await cache_message(
                redis,
                CachedMessageDTO.model_validate(message),
            )

    for message in messages:
        await websocket.send_text(f"{message.sender.username}: {message.message}")

    try:
        while True:
            data = await websocket.receive_text()

            sender = await AsyncORM.users.get(sender_id)

            await cache_message(
                redis,
                CachedMessageDTO(
                    id=None,
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    message=data,
                    sender=UserDTO.model_validate(sender),
                    timestamp=None,
                ),
            )

            sent = await manager.send_personal_message(
                f"{sender.username}: {data}", receiver_id
            )
            if not sent:
                celery_app = websocket.app.state.celery
                receiver = await AsyncORM.users.get(receiver_id)
                if receiver.tg_user_id:
                    celery_app.send_task(
                        "tasks.SendMessageToTG",
                        args=[receiver.tg_user_id, sender.username, data],
                    )

    except WebSocketDisconnect:
        manager.disconnect(sender_id)

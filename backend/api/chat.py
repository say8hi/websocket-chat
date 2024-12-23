from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from misc.connection_manager import ConnectionManager
from schemas.messages import CachedMessageDTO
from schemas.users import UserDTO
from utils.cache import cache_message, get_cached_messages

from database.orm import AsyncORM

manager = ConnectionManager()

chat_router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)


@chat_router.websocket("/ws/{sender_id}/{receiver_id}")
async def websocket_chat(
    websocket: WebSocket,
    sender_id: int,
    receiver_id: int,
):
    await manager.connect(websocket, sender_id)

    redis = websocket.app.state.redis

    # Retrieve cached messages from Redis or fetch from the database if not available
    messages = await get_cached_messages(redis, sender_id, receiver_id)
    if not messages:
        messages = await AsyncORM.messages.get_chat_history(sender_id, receiver_id)
        for message in messages:
            await cache_message(
                redis,
                CachedMessageDTO.model_validate(message),
            )

    # Send existing messages to the connected user
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

            # Send the message to the intended recipient
            sent = await manager.send_personal_message(
                f"{sender.username}: {data}", receiver_id
            )

            # If the recipient is not connected, send a message to their Telegram
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

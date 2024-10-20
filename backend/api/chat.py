from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from database.orm import AsyncORM
from misc.connection_manager import ConnectionManager
from schemas.messages import MessageInDBBaseDTO


manager = ConnectionManager()

chat_router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)


@chat_router.get(
    "/history/{sender_id}/{receiver_id}", response_model=List[MessageInDBBaseDTO]
)
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

    try:
        while True:
            data = await websocket.receive_text()

            await AsyncORM.messages.create(
                sender_id=sender_id, receiver_id=receiver_id, message=data
            )
            sender = await AsyncORM.users.get(sender_id)

            await manager.send_personal_message(
                f"{sender.username}: {data}", receiver_id
            )

    except WebSocketDisconnect:
        manager.disconnect(sender_id)

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections for real-time communication"""

    def __init__(self):
        """Dictionary to keep track of active connections"""
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept a new WebSocket connection and store it"""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        """Remove a WebSocket connection from the active connections"""
        self.active_connections.pop(user_id, None)

    async def send_personal_message(self, message: str, receiver_id: int):
        """Send a personal message to a specific user"""
        receiver_ws = self.active_connections.get(receiver_id)
        if not receiver_ws:
            return False

        await receiver_ws.send_text(message)
        return True

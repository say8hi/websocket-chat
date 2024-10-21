from typing import Optional
from pydantic import BaseModel


class StatusResponse(BaseModel):
    status: str
    data: Optional[dict] = {}


class ConnectTG(BaseModel):
    user_id: int
    tg_user_id: int

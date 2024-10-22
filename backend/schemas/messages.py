from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from schemas.users import UserDTO


class MessageBaseDTO(BaseModel):
    sender_id: int
    receiver_id: int
    message: str


class MessageCreateDTO(MessageBaseDTO):
    pass


class MessageInDBBaseDTO(MessageBaseDTO):
    model_config = ConfigDict(from_attributes=True)
    id: int
    timestamp: datetime
    sender: UserDTO


class CachedMessageDTO(MessageBaseDTO):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int]
    timestamp: Optional[datetime]
    sender: UserDTO


class MessageDTO(MessageInDBBaseDTO):
    pass

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserBaseDTO(BaseModel):
    username: str
    password: str


class UserCreateDTO(UserBaseDTO):
    pass


class UserUpdateDTO(UserBaseDTO):
    username: Optional[str]
    full_name: Optional[str]


class UserInDBBaseDTO(UserBaseDTO):
    model_config = ConfigDict(from_attributes=True)
    id: int
    registered_at: datetime


class UserDTO(UserInDBBaseDTO):
    pass


class StatusResponse(BaseModel):
    status: str
    data: Optional[dict] = {}

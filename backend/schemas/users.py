from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserBaseDTO(BaseModel):
    username: str


class UserRegisterDTO(BaseModel):
    username: str
    password: str


class UserCreateDTO(UserBaseDTO):
    pass


class UserInDBBaseDTO(UserBaseDTO):
    model_config = ConfigDict(from_attributes=True)
    id: int
    registered_at: datetime
    tg_user_id: Optional[int]
    hashed_password: str


class UserDTO(UserInDBBaseDTO):
    pass

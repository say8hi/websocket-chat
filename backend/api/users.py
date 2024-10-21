from typing import List

from fastapi import APIRouter, HTTPException
from fastapi_cache.decorator import cache

from database.orm import AsyncORM
from schemas.users import UserBaseDTO, UserDTO
from schemas.others import StatusResponse, ConnectTG

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@user_router.get("/", response_model=List[UserDTO])
async def get_users():
    users = await AsyncORM.users.get_all()
    return users


@cache(expire=60)
@user_router.get("/{user_id}", response_model=UserDTO)
async def get_user(user_id: int):
    user = await AsyncORM.users.get(user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return user


@user_router.post("/register/", response_model=UserDTO)
async def create_user(user_data: UserBaseDTO):
    try:
        user = await AsyncORM.users.create(**user_data.__dict__)
    except Exception:
        raise HTTPException(status_code=400, detail="Username is already taken")

    return user


@user_router.post("/login/", response_model=UserDTO)
async def login_user(user_data: UserBaseDTO):
    user = await AsyncORM.users.get_filter_by(**user_data.__dict__)
    if user and len(user) == 1:
        return user[0]

    raise HTTPException(status_code=400, detail="User not found")


@user_router.post("/connect-tg", response_model=StatusResponse)
async def connect_tg(user_data: ConnectTG):
    await AsyncORM.users.update(user_data.user_id, tg_user_id=user_data.tg_user_id)

    return StatusResponse(status="ok", data={"message": "successfully connected"})

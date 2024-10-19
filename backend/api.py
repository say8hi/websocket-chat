from asyncio.futures import logging
from fastapi import APIRouter, FastAPI, HTTPException
from database.orm import AsyncORM
from typing import List

from schemas.users import (
    StatusResponse,
    UserBaseDTO,
    UserDTO,
    UserUpdateDTO,
)


app = FastAPI(title="API Example")

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@user_router.get("/", response_model=List[UserDTO])
async def get_users():
    users = await AsyncORM.users.get_all()
    return users


@user_router.get("/{user_id}", response_model=UserDTO)
async def get_user(user_id: int):
    user = await AsyncORM.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.post("/register/", response_model=StatusResponse)
async def create_user(user_data: UserBaseDTO):
    logging.info(user_data)
    user = await AsyncORM.users.create(**user_data.__dict__)
    return StatusResponse(status="ok", data={"user_id": user.id})


@user_router.put("/{user_id}", response_model=UserDTO)
async def update_user(user_id: int, user_data: UserUpdateDTO):
    user = await AsyncORM.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = await AsyncORM.users.update(user_id, **user_data.__dict__)
    return user


@user_router.delete("/{user_id}", response_model=StatusResponse)
async def delete_user(user_id: int):
    user = await AsyncORM.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await AsyncORM.users.delete(user_id)
    return StatusResponse(status="ok", data={"msg": f"User {user_id} was deleted"})

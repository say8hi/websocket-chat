from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_cache.decorator import cache

from database.orm import AsyncORM
from schemas.users import UserDTO
from schemas.others import StatusResponse, ConnectTG
from utils.auth import create_access_token

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


@user_router.post("/register/", response_model=StatusResponse)
async def create_user(
    request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    try:
        pwd_context = request.app.state.pwd_context
        hashed_password = pwd_context.hash(form_data.password)
        user = await AsyncORM.users.create(
            username=form_data.username, hashed_password=hashed_password
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Username is already taken")

    config = request.app.state.config

    # Create an access token for the newly registered user
    access_token = create_access_token(
        data={"sub": {"user_id": user.id, "username": form_data.username}},
        secret_key=config.secrets.auth,
    )

    return StatusResponse(status="ok", data={"token": access_token, "user_id": user.id})


@user_router.post("/login/", response_model=StatusResponse)
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = await AsyncORM.users.get_filter_by(username=form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Wrong username or password")

    user = user[0]

    pwd_context = request.app.state.pwd_context
    if not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong username or password")

    config = request.app.state.config

    # Generate an access token upon successful login
    access_token = create_access_token(
        data={"sub": {"user_id": user.id, "username": form_data.username}},
        secret_key=config.secrets.auth,
    )

    return StatusResponse(status="ok", data={"token": access_token, "user_id": user.id})


# Endpoint to connect a user to Telegram | Used by tg_bot
@user_router.post("/connect-tg", response_model=StatusResponse)
async def connect_tg(user_data: ConnectTG):
    await AsyncORM.users.update(user_data.user_id, tg_user_id=user_data.tg_user_id)

    return StatusResponse(status="ok", data={"message": "successfully connected"})

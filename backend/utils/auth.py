from fastapi import HTTPException, Request
from database.orm import AsyncORM
import jwt
from datetime import datetime, timedelta

from schemas.others import TokenData
from schemas.users import UserDTO


def create_access_token(
    data: dict, secret_key: str, expires_delta: timedelta | None = None
):
    """
    Creates a new access token for user authentication with an expiration time
    """
    to_encode = data.copy()
    expire = datetime.now() + (
        expires_delta if expires_delta else timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encoded_jwt


async def get_current_user(request: Request):
    """
    Retrieves the current user based on the provided token in the request
    """
    oauth2_scheme = request.app.state.oauth2_scheme
    token = await oauth2_scheme(request)
    config = request.app.state.config

    try:
        payload = jwt.decode(token, config.secrets.auth, algorithms=["HS256"])
        sub = payload["sub"]
        if sub is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        token_data = TokenData(user_id=sub.get("user_id"), username=sub.get("username"))
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = await AsyncORM.users.get(token_data.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return UserDTO.model_validate(user)

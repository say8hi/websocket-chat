import asyncio
import logging
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
import uvicorn
from celery import Celery
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from api import routers_list
from config import load_config
from database.orm import AsyncORM
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext


async def setup_database(config):
    """Establishes a connection to the PostgreSQL database and initializes the ORM"""
    while True:
        try:
            async_engine = create_async_engine(
                url=f"postgresql+asyncpg://{config.postgres.db_user}:{config.postgres.db_pass}"
                f"@{config.postgres.db_host}:5432/{config.postgres.db_name}",
                # echo=True,
            )
            async_session_factory = async_sessionmaker(async_engine)
            AsyncORM.set_session_factory(async_session_factory)
            AsyncORM.init_models()
            await AsyncORM.create_tables(async_engine)

            break
        except Exception:
            await asyncio.sleep(1)

    logging.info("Successfully connected to Database")


async def setup_redis(config):
    """Establishes a connection to the Redis server for caching"""
    redis_client = aioredis.from_url(config.redis.dsn())
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    return redis_client


async def setup_celery(config):
    """Initialise celery"""
    celery_app = Celery(
        "chat_tasks",
        broker=f"redis://:{config.redis.redis_pass}@{config.redis.redis_host}:{config.redis.redis_port}/1",
        backend=f"redis://:{config.redis.redis_pass}@{config.redis.redis_host}:{config.redis.redis_port}/0",
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
    return celery_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    config = load_config(".env")

    await setup_database(config)
    redis = await setup_redis(config)
    celery_app = await setup_celery(config)

    # Auth
    app.state.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    app.state.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

    app.state.redis = redis
    app.state.celery = celery_app
    app.state.config = config

    for router in routers_list:
        app.include_router(router)

    yield

    # Shutdown
    await FastAPICache.clear()
    await AsyncORM.session_factory().close()


if __name__ == "__main__":
    app = FastAPI(title="API Example", lifespan=lifespan)

    uvicorn.run(app, host="0.0.0.0", port=8000)

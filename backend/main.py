import asyncio
from contextlib import asynccontextmanager
import logging
from celery import Celery
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from api.users import user_router
from api.chat import chat_router
import uvicorn

from config import load_config
from database.orm import AsyncORM

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as aioredis


async def setup_database(config):
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
            break
        except Exception:
            await asyncio.sleep(1)

    logging.info("Successfully connected to Database")
    return async_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config(".env")

    # Initialise Database
    engine = await setup_database(config)
    await AsyncORM.create_tables(engine)

    # Initialise redis
    redis = await aioredis.from_url(
        f"redis://:{config.redis.redis_pass}@{config.redis.redis_host}:{config.redis.redis_port}/0",
        encoding="utf8",
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

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

    app.state.redis = redis
    app.state.celery = celery_app

    yield


if __name__ == "__main__":
    app = FastAPI(title="API Example", lifespan=lifespan)
    app.include_router(user_router)
    app.include_router(chat_router)

    uvicorn.run(app, host="0.0.0.0", port=8000)

from celery import Celery

from environs import Env

env = Env()
env.read_env()

redis_pass = env.str("REDIS_PASSWORD")
redis_port = env.int("REDIS_PORT")
redis_host = env.str("REDIS_HOST")


celery_app = Celery(
    "chat_tasks",
    broker=f"redis://:{redis_pass}@{redis_host}:{redis_port}/1",
    backend=f"redis://:{redis_pass}@{redis_host}:{redis_port}/0",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

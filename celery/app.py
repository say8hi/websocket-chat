from celery import Celery
from environs import Env
from tasks import SendMessageToTG

env = Env()
env.read_env()

redis_pass = env.str("REDIS_PASSWORD")
redis_port = env.int("REDIS_PORT")
redis_host = env.str("REDIS_HOST")

tgbot_token = env.str("BOT_TOKEN")


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


notify_tg = SendMessageToTG(tgbot_token)
celery_app.register_task(notify_tg)

import json
from redis.asyncio.client import Redis
from database.orm import AsyncORM
from schemas.messages import CachedMessageDTO


def get_cache_key(sender_id: int, receiver_id: int):
    return f"chat:{min(sender_id, receiver_id)}:{max(sender_id, receiver_id)}"


async def get_cached_messages(redis_client: Redis, sender_id: int, receiver_id: int):
    cache_key = get_cache_key(sender_id, receiver_id)
    cached_messages = await redis_client.lrange(cache_key, 0, -1)
    return [
        CachedMessageDTO.model_validate(json.loads(msg.decode("utf-8")))
        for msg in cached_messages
    ]


async def cache_message(redis_client: Redis, message: CachedMessageDTO):
    cache_key = get_cache_key(message.sender_id, message.receiver_id)

    await redis_client.rpush(cache_key, message.model_dump_json())

    if await redis_client.llen(cache_key) > 10:
        messages = await get_cached_messages(
            redis_client, message.sender_id, message.receiver_id
        )
        await AsyncORM.messages.add_cached_messages(messages)
        await redis_client.delete(cache_key)
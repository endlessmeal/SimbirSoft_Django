import secrets

import aioredis

from API.app.config import redis_port, redis_host, token_ttl


async def token_is_valid(email, token, redis):
    stored_token = await redis.get(email, encoding="utf-8")

    return stored_token == token


async def store_token(email, token, redis):
    await redis.set(email, token)
    await redis.expire(email, int(token_ttl))


async def remove_token(email, redis):
    await redis.delete(email)


def create_token():
    return secrets.token_hex(32)


async def make_redis_pool():
    redis_address = (redis_host, redis_port)
    return await aioredis.create_redis_pool(redis_address)

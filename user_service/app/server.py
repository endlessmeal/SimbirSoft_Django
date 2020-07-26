import aiohttp_session
from aiohttp import web
from views import signin, login, get_user_info, get_new_tokens, logout
from aiopg.sa import create_engine
import aioredis
from aiohttp_session.redis_storage import RedisStorage
import asyncio
from settings import DATABASE, REDIS
from aiohttp_swagger import setup_swagger

conf = {
    "postgres": {
        "host": DATABASE['HOST'],
        "port": DATABASE['PORT'],
        "user": DATABASE['USER'],
        "password": DATABASE['PASSWORD'],
        "database": DATABASE['DATABASE'],
        "minsize": 1,
        "maxsize": 10,
        "echo": True,
        "timeout": 60
    }
}


async def init_pg(app):
    conf = app['config']['postgres']
    engine = await create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
        loop=app.loop)
    app['db'] = engine


async def make_redis_pool():
    redis_address = (REDIS['HOST'], REDIS['PORT'])
    return await aioredis.create_pool(
        redis_address,
        create_connection_timeout=1,
    )


def make_app():
    loop = asyncio.get_event_loop()
    redis_pool = loop.run_until_complete(make_redis_pool())
    storage = RedisStorage(redis_pool)
    session_middleware = aiohttp_session.session_middleware(storage)

    app = web.Application(middlewares=[session_middleware])
    app['config'] = conf
    app.router.add_post('/api/v1/signin', signin)
    app.router.add_post('/api/v1/login', login)
    app.router.add_get('/api/v1/info', get_user_info)
    app.router.add_get('/api/v1/newtokens', get_new_tokens)
    app.router.add_get('/api/v1/logout', logout)
    setup_swagger(app,
                  title='User authentication',
                  description='User service with OAuth2.0',
                  api_version="1",
                  swagger_url="/api/v1/doc",
                  ui_version=1)
    app.on_startup.append(init_pg)
    return app


web.run_app(make_app())


from .server import get_app

# import asyncio
# from messages.app.amqp.listener import listener

app = get_app()

#
# @app.on_event("startup")
# def startup():
#     loop = asyncio.get_event_loop()
#     asyncio.ensure_future(listener(loop))

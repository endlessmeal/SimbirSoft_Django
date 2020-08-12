import aio_pika
from dotenv import load_dotenv
from ..config import BROKER_CONN_URI
load_dotenv()


async def publisher(msg):
    connection = await aio_pika.connect(BROKER_CONN_URI, port=5672)

    routing_key = "messages"

    channel = await connection.channel()

    await channel.default_exchange.publish(
        aio_pika.Message(body=msg.encode()), routing_key=routing_key,
    )

    await connection.close()

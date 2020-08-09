import aio_pika


async def publisher(msg):
    connection = await aio_pika.connect("amqp://guest:guest@rabbit/", port=5672)

    routing_key = "messages"

    channel = await connection.channel()

    await channel.default_exchange.publish(
        aio_pika.Message(body=msg.encode()), routing_key=routing_key,
    )

    await connection.close()

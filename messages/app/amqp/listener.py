import asyncio
import aio_pika
import aiosmtplib
from email.message import EmailMessage
import json
from messages.app.config import (
    SENDER,
    SMTP_PORT,
    BROKER_CONN_URI,
    RABBIT_PORT,
    QUEUE_NAME,
    MAX_COUNT,
)


async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        email_message = EmailMessage()
        msg = json.loads(message.body.decode("utf-8"))
        email_message["From"] = SENDER
        email_message["To"] = msg["to"]
        email_message["Subject"] = msg["subject"]
        email_message.set_content(msg["text"])

        await aiosmtplib.send(email_message, hostname="mail", port=SMTP_PORT)


async def listener(loop):
    connection = await aio_pika.connect_robust(
        BROKER_CONN_URI, loop=loop, port=RABBIT_PORT,
    )

    queue_name = QUEUE_NAME

    # Creating channel
    channel = await connection.channel()

    # Maximum message count which will be
    # processing at the same time.
    await channel.set_qos(prefetch_count=int(MAX_COUNT))

    # Declaring queue
    queue = await channel.declare_queue(queue_name)

    await queue.consume(process_message)

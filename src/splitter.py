import asyncio
from broker import broker

async def split_them_messages():
    while True:
        await broker.publish("news", "Breaking news: Something happened!")
        await asyncio.sleep(2)
import asyncio
from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.tl.types import Message


async def main():
    client = TelegramClient(session='parser', api_id=29025867, api_hash='f8fc15aba39ffc84db23827582b0f723',
                            system_version='4.16.30-vxCUSTOM"', device_model='Iphone 15',
                            app_version='10.10.10'
                            )

    await client.start()

    @client.on(NewMessage())
    async def parse(event: Message):
        print(event)

    await client.run_until_disconnected()


if __name__ == '__main__':
    asyncio.run(main())

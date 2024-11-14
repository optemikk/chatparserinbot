# -*- coding: utf-8 -*-
import asyncio
import platform
from aiogram import Bot, Dispatcher
from config import API_KEY

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

tgbot = Bot(token=API_KEY)
dp = Dispatcher()


from bot.user_interface.loader import router as user_interface_router


dp.include_routers(user_interface_router)


async def main() -> None:
    await dp.start_polling(tgbot)


if __name__ == '__main__':
    asyncio.run(main())

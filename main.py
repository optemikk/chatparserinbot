# from chat_parser.chatparser import *
from bot.loader import *
from database.database import db
from session_organizer import organizer


async def start_timer():
    await db.update_days_data()

async def setup_sessions():
    await organizer.load_sessions()

async def start_bot():
    await dp.start_polling(tgbot)


async def main():
    await asyncio.gather(start_bot(), start_timer(), setup_sessions())


if __name__ == '__main__':
    asyncio.run(main())

import sqlite3
from ast import parse
from datetime import datetime, timedelta
import asyncio

from bot.loader import tgbot


class Database:
    def __init__(self):
        self.db = sqlite3.connect(database=r'database/database.db')
        self.c = self.db.cursor()

        self.users: list[list] = list()

        self.c.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INT,
                        subscription INT,
                        is_parsing INT,
                        status TEXT,
                        trial_sub INT,
                        full_name TEXT,
                        interval INT,
                        prev_interval INT
                    )''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS keywords (
                                is_stop INT,
                                user_id INT,
                                keyword INT,
                                parse_mode TEXT DEFAULT "default"
                            )''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS sessions (
                                session TEXT,
                                api_id INT,
                                api_hash TEXT,
                                phone TEXT,
                                full_name TEXT,
                                is_banned INT
                            )''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS sources (
                                        session TEXT,
                                        url TEXT,
                                        title TEXT,
                                        chat_id INT
                                    )''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS parsed_messages (
                                        url TEXT,
                                        message_text TEXT,
                                        to_user INT,
                                        match TEXT
                                    )''')

    async def add_user(self, user_id: int, full_name: str):
        self.c.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (user_id, 0, 0, 'user', 0, full_name, 0, 0))
        self.db.commit()

    async def set_interval(self, user_id: int, interval: int):
        self.c.execute('UPDATE users SET interval = (?) WHERE user_id = (?)', (interval, user_id))
        self.db.commit()

    async def set_prev_interval(self, user_id: int, interval: int):
        self.c.execute('UPDATE users SET prev_interval = (?) WHERE user_id = (?)', (interval, user_id))
        self.db.commit()

    async def get_parsed_messages(self, user_id: int):
        messages = self.c.execute('SELECT * FROM parsed_messages WHERE to_user = (?)', (user_id,)).fetchall()
        return messages

    async def set_admin(self, user_id: int):
        self.c.execute('UPDATE users SET status = ("admin") WHERE user_id = (?)', (user_id,))
        self.db.commit()

    async def add_key_string(self, is_stop: int, user_id: int, keyword: str, parse_mode: str):
        if await self.is_keyword_exists(user_id=user_id, keyword=keyword):
            return
        self.c.execute('INSERT INTO keywords VALUES (?, ?, ?, ?)', (is_stop, user_id, keyword, parse_mode))
        self.db.commit()

    async def is_user_exists(self, user_id: int):
        user = self.db.execute('SELECT * FROM users WHERE user_id = (?)', (user_id,)).fetchone()
        if user:
            return True
        return False

    async def change_parsing(self, user_id: int):
        # is_parsing = await self.is_user_parsing(user_id)
        self.c.execute('UPDATE users SET is_parsing = (NOT is_parsing) WHERE user_id = (?)', (user_id,))
        self.db.commit()

    async def get_sub_to(self, user_id: int):
        sub_to = self.c.execute('SELECT subscription FROM users WHERE user_id = (?)', (user_id,)).fetchone()[0]
        return sub_to

    async def get_keywords(self, user_id: int):
        keywords = self.c.execute('SELECT keyword FROM keywords WHERE user_id = (?) AND is_stop = 0', (user_id,)).fetchall()
        return [i[0] for i in keywords]

    async def get_stop_keywords(self, user_id: int):
        keywords = self.c.execute('SELECT keyword FROM keywords WHERE user_id = (?) AND is_stop = 1', (user_id,)).fetchall()
        return [i[0] for i in keywords]

    async def delete_all_keywords(self, user_id: int, is_stop: int):
        self.c.execute('DELETE FROM keywords WHERE user_id = (?) AND is_stop = (?)', (user_id, is_stop))
        self.db.commit()

    async def is_admin(self, user_id: int):
        status = self.c.execute('SELECT status FROM users WHERE user_id = (?)', (user_id,)).fetchone()[0]
        return status == 'admin'

    async def is_user_parsing(self, user_id: int):
        parsing_status = self.c.execute('SELECT is_parsing FROM users WHERE user_id = (?)', (user_id,)).fetchone()[0]
        return parsing_status

    async def is_keyword_exists(self, user_id: int, keyword: str):
        word = self.c.execute('SELECT * FROM keywords WHERE user_id = (?) AND keyword = (?)', (user_id, keyword)).fetchone()
        if word:
            return True
        return False

    async def get_admins(self):
        admins = self.c.execute('SELECT user_id FROM users WHERE status = "admin"').fetchall()
        return [i[0] for i in admins]

    async def is_user_trial(self, user_id: int):
        trial = self.c.execute('SELECT trial_sub FROM users WHERE user_id = (?)', (user_id,)).fetchone()[0]
        return trial

    async def change_user_trial(self, user_id: int):
        self.c.execute('UPDATE users SET trial_sub = 1 WHERE user_id = (?)', (user_id,))
        self.db.commit()

    async def set_user_sub_date(self, user_id: int, date: int):
        to_sub_date = datetime.now().timestamp() + date
        self.c.execute('UPDATE users SET subscription = (?) WHERE user_id = (?)', (to_sub_date, user_id))
        self.db.commit()

    async def set_parser(self, user_id: int):
        self.c.execute('UPDATE users SET status = "parser" WHERE user_id = (?)', (user_id,))
        self.db.commit()

    async def get_parser_accounts(self):
        accounts = self.c.execute('SELECT user_id FROM users WHERE status = "parser"').fetchall()
        result = [i[0] for i in accounts]
        print(result)
        print([result])
        return result

    async def add_session(self, session: str, api_id: int, api_hash: str, phone: str, full_name: str):
        self.c.execute('INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?)', (session, api_id, api_hash, phone, full_name, 0))
        self.db.commit()

    async def add_source(self, session: str, source_url: str, source_title: str, source_chat_id: int):
        if not await self.is_source_exists(source_chat_id):
            self.c.execute('INSERT INTO sources VALUES (?, ?, ?, ?)', (session, source_url, source_title, source_chat_id))
            self.db.commit()

    async def is_source_exists(self, chat_id: int):
        source = self.c.execute('SELECT * FROM sources WHERE source_chat_id = (?)', (chat_id,)).fetchone()
        if source:
            return True
        return False

    async def get_all_sessions(self):
        sessions = self.c.execute('SELECT * FROM sessions').fetchall()
        return sessions

    async def get_unbanned_sessions(self):
        sessions = self.c.execute('SELECT * FROM sessions WHERE is_banned = 0').fetchall()
        return sessions

    async def get_source_by_chat_id(self, chat_id: int):
        session = self.c.execute('SELECT session FROM sources WHERE source_chat_id = (?)', (chat_id,)).fetchone()[0]
        return session

    async def get_all_keywords(self):
        keywords = self.c.execute('SELECT user_id, keyword, parse_mode FROM keywords WHERE is_stop = 0'). fetchall()
        return keywords

    async def get_all_stop_keywords(self):
        keywords = self.c.execute('SELECT user_id, keyword, parse_mode FROM keywords WHERE is_stop = 1'). fetchall()
        return keywords

    async def get_users(self):
        users = self.c.execute('SELECT user_id FROM users WHERE status = "user"').fetchall()
        return users

    async def get_all_user_data(self):
        users = self.c.execute('SELECT * FROM users WHERE status = "user"').fetchall()
        return users

    async def get_sources(self):
        sources = self.c.execute('SELECT * FROM sources').fetchall()
        return sources

    async def update_days_data(self):
        while True:
            now = round(datetime.now().timestamp())
            users = self.c.execute('SELECT * FROM users').fetchall()
            for user in users:
                # print(user)
                if user[1] != 0:
                    if user[5] != 0 and (now - user[7]) > (user[6] * 60):
                        self.c.execute('UPDATE users SET prev_interval = (?) WHERE user_id = (?)', (now, user[0]))
                        messages = self.c.execute('SELECT * FROM parsed_messages WHERE to_user = (?)', (user[0],)).fetchall()
                        self.c.execute('DELETE FROM parsed_messages WHERE to_user = (?)', (user[0],))
                        self.db.commit()
                        for message in messages:
                            await tgbot.send_message(chat_id=user[0], text=f'Ссылка на сообщение: {message[0]}\n'
                                                                           f'Совпадение - {"полное" if message[3] == "full" else "неполное"}\n'
                                                                           f'---------------------------------\n'
                                                                           f'Текст сообщения:\n'
                                                                           f'{message[1]}')
                    if user[1] <= now and user[1] != '0':
                        self.c.execute('UPDATE users SET subscription = "0" WHERE user_id = (?)', (user[0],))
                        self.c.execute('UPDATE users SET is_parsing = 0 WHERE user_id = (?)', (user[0],))
                        self.db.commit()

            await asyncio.sleep(60)

    async def add_parsed_message(self, url: str, text: str, to_user: int, match: str):
        self.c.execute('INSERT INTO parsed_messages VALUES (?, ?, ?, ?)', (url, text, to_user, match))
        self.db.commit()

    # async def get_parsed_messages(self, chat_id: int):
    #     messages = self.c.execute('SELECT * FROM parsed_messages WHERE chat_id = (?)', (chat_id,)).fetchall()
    #     return messages

db = Database()
# db.add_settings()

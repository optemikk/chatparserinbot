import asyncio

from chat_parser.chatparser import ChatParser
from database.database import db
from telethon import TelegramClient, events

import os


class SessionOrganizer:
    def __init__(self):
        self.sessions: list[ChatParser] = list()
        self.account_cache = dict()

    async def load_sessions(self):
        self.sessions = list()
        sessions = os.listdir('chat_parser/sessions')

        selected_sessions = list()
        for session in sessions:
            if 'journal' in session:
                continue
            selected_sessions.append(session.split('.')[0])

        for session in selected_sessions:
            parser = ChatParser()

            flag_words = await db.get_all_keywords()
            ban_words = await db.get_all_stop_keywords()

            for word in ban_words:
                if word[0] not in parser.ban_words:
                    parser.ban_words[word[0]] = list()
                parser.ban_words[word[0]].append((word[1], word[2]))
            requires = dict()
            for user in parser.ban_words:
                if user not in requires:
                    requires[user] = 0
                for words in parser.ban_words[user]:
                    if words[1] == 'required':
                        requires[user] += 1
            parser.ban_requires = requires

            for word in flag_words:
                if word[0] not in parser.flag_words:
                    parser.flag_words[word[0]] = list()
                parser.flag_words[word[0]].append((word[1], word[2]))
            requires = dict()
            for user in parser.flag_words:
                if user not in requires:
                    requires[user] = 0
                for words in parser.flag_words[user]:
                    if words[1] == 'required':
                        requires[user] += 1
            parser.flag_requires = requires

            if session not in parser.sessions_names:
                client = TelegramClient(session=f'chat_parser/sessions/' + session, api_id=29025867,
                                        api_hash='f8fc15aba39ffc84db23827582b0f723',
                                        system_version='4.16.30-vxCUSTOM"', device_model='Iphone 15',
                                        app_version='10.10.10')
                await client.start()
                parser.parser_client = client
                parser.handlers.append(parser.parser_client.add_event_handler(parser.parser_message_handler, events.NewMessage()))

            self.sessions.append(parser)

    async def add_keyword(self, word: str, flag: str, user_id: int, parse_mode: str):
        for session in self.sessions:
            match flag:
                case 'key':
                    session.flag_words[user_id].append((word, parse_mode))
                    requires = dict()
                    for user in session.flag_words:
                        if user not in requires:
                            requires[user] = 0
                        for words in session.flag_words[user]:
                            print(words)
                            if words[1] == 'required':
                                requires[user] += 1
                    session.flag_requires = requires
                case 'stop':
                    session.ban_words[user_id].append((word, parse_mode))
                    requires = dict()
                    for user in session.ban_words:
                        if user not in requires:
                            requires[user] = 0
                        for words in session.ban_words[user]:
                            if words[1] == 'required':
                                requires[user] += 1
                    session.ban_requires = requires

    async def add_account(self, session: str, user_id: int, api_id: int, api_hash: str):
        self.account_cache[user_id] = {'client': TelegramClient(session=f'chat_parser/sessions/{session}',
                                                                api_id=api_id, api_hash=api_hash,
                                                                system_version='4.16.30-vxCUSTOM"',
                                                                device_model='Iphone 15',
                                                                app_version='10.10.10'),
                                       'api_id': api_id,
                                       'api_hash': api_hash}
        print(self.account_cache)

    async def start_account(self, user_id: int, phone: str):
        print(self.account_cache)
        client: TelegramClient = self.account_cache[user_id]['client']
        await client.connect()
        await asyncio.sleep(2)
        await client.send_code_request(phone=phone)

    async def enter_code(self, user_id: int, code: str):
        client: TelegramClient = self.account_cache[user_id]['client']
        await client.sign_in(code=code)
        await asyncio.sleep(3)
        await client.start()
        parser = ChatParser()
        flag_words = await db.get_all_keywords()
        ban_words = await db.get_all_stop_keywords()

        [parser.ban_words.append(word) for word in ban_words]
        [parser.flag_words.append(word) for word in flag_words]
        parser.handlers.append(client.add_event_handler(parser.parser_message_handler, events.NewMessage()))
        parser.parser_client = client
        self.sessions.append(parser)
        return True


organizer = SessionOrganizer()

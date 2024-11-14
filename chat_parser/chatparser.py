from telethon import TelegramClient
from telethon.tl.types import Message, UpdateNewChannelMessage, PeerChannel
from database.database import db
import asyncio
import os


class ChatParser:
    def __init__(self):
        self.sessions_names = list()
        self.parser_client: TelegramClient | None = None

        # self.parsing_chats: dict[int: str] = dict()

        self.flag_words: dict[int: list[tuple[str, str]]] = dict()
        self.flag_requires: dict[int: int] = dict()
        self.ban_words: dict[int: list[tuple[str, str]]] = dict()
        self.ban_required: dict[int: int]

        self.handlers = list()

    async def parser_message_handler(self, event):
        if type(event.original_update) == UpdateNewChannelMessage:
            event: Message = event.message
            message_text = event.message.lower()
            message_id = event.id

            for user in self.ban_words:
                for ban in self.ban_words[user]:
                    if ban[0] in message_text:
                        print('ban detected')
                        return

            for user in self.flag_words:
                print(user)
                print(self.flag_requires)
                print(self.flag_requires[user] == 0)
                if self.flag_requires[user] == 0:
                    for flag in self.flag_words[user]:
                        if flag[0] in message_text:
                            match type(event.peer_id):
                                case PeerChannel:
                                    from_id = event.peer_id.channel_id
                            await db.add_parsed_message(url=f'https://t.me/c/{from_id}/{message_id}',
                                                        text=event.message,
                                                        to_user=flag[0],
                                                        match='full')
                else:
                    user_matches = 0
                    for flag in self.flag_words[user]:
                        if flag[0] in message_text:
                            if flag[1] == 'required':
                                user_matches += 1
                    match type(event.peer_id):
                        case PeerChannel:
                            from_id = event.peer_id.channel_id
                    if user_matches > 1:
                        await db.add_parsed_message(url=f'https://t.me/c/{from_id}/{message_id}',
                                                    text=event.message,
                                                    to_user=user,
                                                    match='full' if user_matches == self.flag_requires[user] else 'partly')



async def main():
    client = TelegramClient(session='parser', api_id=29025867, api_hash='f8fc15aba39ffc84db23827582b0f723')
    await client.start()


if __name__ == '__main__':
    asyncio.run(main())

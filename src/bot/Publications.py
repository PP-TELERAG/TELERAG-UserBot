
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message


class Publications:
    def __init__(self, client: Client, subsctiptions: set[int] = None, history_limit: int = 5):
        self.client = client
        self.subsctiptions = subsctiptions
        self.publications = {}
        self.history_limit = history_limit
        self.message_handler = MessageHandler(
            self.__new_message_handler, filters.chat(self.subsctiptions))

    async def __new_message_handler(self, client: Client, message: Message):
        if message.chat.id in self.subsctiptions:
            text = message.text or "<no text>"
            self.publications[message.chat.id] = text
        # Здесь будет также отправка сообщения сразу же в хендлер подключения к другим сервисам для дальнейшего чанкования

    async def __fetch_past_messages(self, channel_id: int):
        async for message in self.client.get_chat_history(channel_id, limit=self.history_limit):
            text = message.text or "<no text>"
            self.publications[message.chat.id] = text

    async def update_subsctiptions(self, new_subsctiptions: set[int]):
        added_channels = new_subsctiptions - self.subsctiptions
        self.subsctiptions = new_subsctiptions

        for channel_id in added_channels:
            await self.__fetch_past_messages(channel_id)

        self.client.remove_handler(self.message_handler)
        self.message_handler = MessageHandler(
            self.__new_message_handler, filters.chat(list(self.subsctiptions)))
        self.client.add_handler(self.message_handler)

    def start(self):
        self.client.add_handler(self.message_handler)
        print("Publications listening start...")
        self.client.run()

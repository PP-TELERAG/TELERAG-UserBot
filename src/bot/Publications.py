from loguru import logger
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
import asyncio

class Publications:
    def __init__(self, client: Client, subsctiptions: set[int]= None, history_limit: int = 5):
        self.client = client
        self.subscriptions = subsctiptions
        self.publications_queue = asyncio.Queue()
        self.history_limit = history_limit
        self.message_handler = MessageHandler(self.__new_message_handler, filters.chat(self.subscriptions))

    async def __new_message_handler(self, client: Client, message: Message):
        try:
            text = message.text or "<no text>"
            logger.info("Gathering message from {}", message.chat.id)
            await self.publications_queue.put((message.chat.id, text))
        except Exception as e:
            logger.exception("Error occurred while gathering message from {}: {}", message.chat.id, e)


    async def __fetch_past_messages(self, channel_id:int):
        async for message in self.client.get_chat_history(channel_id, limit=self.history_limit):
            try:
                text = message.text or "<no text>"
                logger.info("Gathering message from {}", message.chat.id)
                await self.publications_queue.put((message.chat.id, text))
            except Exception as e:
                logger.exception("Error occurred while gathering message from {}: {}",message.chat.id, e)


    async def update_subscriptions(self, new_subscriptions: set[int]):
        added_channels = new_subscriptions - self.subscriptions
        self.subscriptions = new_subscriptions

        for channel_id in added_channels:
            await self.__fetch_past_messages(channel_id)

        self.client.remove_handler(self.message_handler)
        self.message_handler = MessageHandler(self.__new_message_handler, filters.chat(list(self.subscriptions)))
        self.client.add_handler(self.message_handler)

    def start(self):
        self.client.add_handler(self.message_handler)
        logger.info("Starting handling new messages...")


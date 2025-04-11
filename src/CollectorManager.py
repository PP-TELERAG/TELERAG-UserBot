from typing import Optional

from pyrogram import Client, filters
from loguru import logger
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
import asyncio

from src.Config import Settings
from src.BrokerGateway import BrokerGateway
from src.Models import *

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class CollectorManager(metaclass=Singleton):
    _instance: Optional["CollectorManager"] = None

    @classmethod
    def get_instance(cls) -> "CollectorManager":
        return cls._instance

    def __init__(self, settings: Settings, client: Client):
        self._gather_task = None

        self.entry_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()
        self.SubscriptionWorker = SubscriptionWorker(
            client,
            upstream_queue=self.output_queue
        )

        self.PublicationWorker = PublicationWorker(
            pyroclient=client,
            upstream_queue=self.output_queue,
            history_limit=settings.COLLECTOR_HISTORY_LIMIT
        )

        self.BrokerGateway = BrokerGateway(
            broker_ulr=settings.BROKER_ULR,
            broker_in_topic=settings.BROKER_IN_TOPIC,
            broker_out_topic=settings.BROKER_OUT_TOPIC
        )

    async def __production_task(self):
        if self.output_queue.empty():
            await asyncio.sleep(0.1)
            return
        try:
            response = await self.output_queue.get()
            if type(response) is not ResponseToRAG and type(response) is not RemoveSourceResponseToRAG:
                logger.warning("Unsupported type of Response {}. Skipping...", type(response))
            await self.BrokerGateway.produce_message_to_broker(response)
            logger.info("Produced message to broker.")
        except Exception as e:
            logger.exception("Exception occurred while producing message to broker: {}", e)
        finally:
            self.output_queue.task_done()
            await asyncio.sleep(0.1)


    async def __subs_task(self):
        if self.output_queue.empty():
            await asyncio.sleep(0.1)
            return
        try:
            task = await self.entry_queue.get()
            if type(task) is SubscribeRequest:
                new_subs_set = await self.SubscriptionWorker.join_chats(task.channels_payload)
                await self.PublicationWorker.subscriptions_updated(new_subs_set)
                logger.info("Changes (New subscriptions) applied successfully.")
            elif type(task) is UnsubscribeRequest:
                new_subs_set = await self.SubscriptionWorker.leave_chats(task.channels_payload)
                await self.PublicationWorker.subscriptions_updated(new_subs_set)
                logger.info("Changes (Leave subscriptions) applied successfully.")
            else:
                logger.warning("Unsupported request type! Skipping...")
        except Exception as e:
            logger.exception("Exception occurred while executing subscription task: {}", e)
        finally:
            self.entry_queue.task_done()
            await asyncio.sleep(0.1)

    async def consume_by_notification(self):
        request = await self.BrokerGateway.consume_subscriptions_worker_task()
        if type(request) is not SubscribeRequest and type(request) is not UnsubscribeRequest:
            logger.warning("Unsupported type of subscription request: {}", type(request))
            return
        await self.entry_queue.put(request)

    async def _production_runloop(self):
        while True:
            await self.__production_task()

    async def _subs_runloop(self):
        while True:
            await self.__subs_task()

    async def start_routines(self):
        self._gather_task = asyncio.create_task(
            asyncio.gather(
                self._subs_runloop(),
                self._production_runloop()
            )
        )
        logger.info("CollectorManager routines started via asyncio.gather method.")

    async def stop_routines(self):
        if self._gather_task is not None:
            self._gather_task.cancel()
            try:
                await self._gather_task
            except asyncio.CancelledError:
                logger.info("CollectorManager routines cancelled.")
        self._gather_task = None

class SubscriptionWorker:

    def __init__(self, pyroclient: Client, upstream_queue: asyncio.Queue):
        self.upstream_queue = upstream_queue
        self.client = pyroclient
        self.subscriptions = dict()


    async def __fetch_subscriptions(self):
        async with self.client as client:
            dialogs = await client.get_dialogs()
            self.subscriptions = {
                dialog.chat.id: 1
                for dialog in dialogs
                if dialog.chat.type in ("channel", "supergroup")
            }

    async def join_chats(self, request: SubscribeRequest) -> set[int]:
        async with self.client as client:
            for channel_id in request.channels_payload:
                if channel_id not in self.subscriptions:
                    try:
                        await client.join_chat(channel_id)
                        logger.info("Joined channel {}", channel_id)
                        self.subscriptions[channel_id] = 1
                    except Exception as e:
                        logger.exception("Exception while joining channel {}: {}", channel_id, e)
                else:
                    logger.info("Already joined channel {}. Incrementing people count...", channel_id)
                    self.subscriptions[channel_id] += 1
        return set(self.subscriptions.keys())

    async def leave_chats(self, request: UnsubscribeRequest) -> set[int]:
        async with self.client as client:
            for channel_id in request.channels_payload:
                if channel_id in self.subscriptions:
                    try:
                        if self.subscriptions[channel_id] > 1:
                            self.subscriptions[channel_id] -= 1
                        else:
                            await client.leave_chat(channel_id)
                            await self.upstream_queue.put(RemoveSourceResponseToRAG(channel_id=channel_id))
                            logger.info("Left channel {}. Also made request to delete source from RAG module.",
                                        channel_id
                                        )
                    except Exception as e:
                        logger.exception("Exception while trying to leave channel {}: {}", channel_id, e)
                else:
                    logger.warning("Unexpected id {}. Already left or never joined in first place.", channel_id)
        return set(self.subscriptions.keys())

    async def validate_chat_id(self, chat_id: int) -> bool:
        async with self.client as client:
            try:
                chat = await client.get_chat(chat_id)
                if chat.type == "private":
                    logger.warning("This id {} is private. Not supported...", chat_id)
                    return False
                if chat.type == "supergroup" or chat.type == "channel":
                    logger.info("Chat {} is channel or supergroup. Valid!", chat_id)
                    return True
                else:
                    logger.warning("Unsupported type of chat {}: {}", chat_id, chat.type)
                    return False
            except Exception as e:
                logger.exception("Exception while trying to validate chat {}: {}", chat_id, e)

    async def on_start(self):
        await self.__fetch_subscriptions()


class PublicationWorker:

    def __init__(self, pyroclient: Client,
            upstream_queue: asyncio.Queue,
            subscriptions: set[int] = None,
            history_limit: int = 100):

        self.client = pyroclient
        self.subscriptions = subscriptions if subscriptions else set()
        self.history_limit = history_limit
        self.upstream_queue = upstream_queue

        self.message_handler = MessageHandler(
            self.__new_messages_collector,
            filters=filters.chat(list(self.subscriptions))
        )

        self.client.add_handler(self.message_handler)

    async def __new_messages_collector(self,message: Message):
        text = message.text or None
        if text:
            collected_message = ResponseToRAG(
                channel_id=message.chat.id,
                texts=text
            )
            await self.upstream_queue.put(collected_message)


    async def __fetch_past_messages(self, chat_id: int):
        async for message in self.client.get_chat_history(chat_id, limit=self.history_limit):
            text = message.text or None
            if text:
                collected_message = ResponseToRAG(
                    channel_id=message.chat.id,
                    texts=text
                )
                await self.upstream_queue.put(collected_message)


    async def subscriptions_updated(self, new_subscriptions: set[int]):
        added_len = len(new_subscriptions) - len(self.subscriptions)
        if added_len > 0:
            logger.info("Adding new channels to handler.")
            added_channels = new_subscriptions - self.subscriptions
            for channel_id in added_channels:
                await self.__fetch_past_messages(channel_id)
        elif added_len == 0:
            logger.info("Nothing to update.")
            return
        elif added_len < 0:
            logger.info("Removing unsubscribed channels from handler.")

        self.subscriptions = new_subscriptions

        self.client.remove_handler(self.message_handler)
        self.message_handler = MessageHandler(self.__new_messages_collector, filters.chat(list(self.subscriptions)))
        self.client.add_handler(self.message_handler)
        logger.info("Updated subscriptions. Started handling messages from them.")

    def on_start(self):
        self.client.add_handler(self.message_handler)



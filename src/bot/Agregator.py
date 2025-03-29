import asyncio
from loguru import logger
from pyrogram import Client
from time import time
from src.config.config import Settings
from src.bot.Router import Router, Response
from src.bot.Publications import Publications
from src.bot.Subscriptions import Subscriptions
from src.bot.Validation import Validation

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Agregator(metaclass=Singleton):
    def __init__(self, configuration: Settings=None, client: Client=None):
        self.Router = Router(broker_url=configuration.BROKER_URL, broker_in_topic=configuration.BROKER_IN_TOPIC, broker_out_topic=configuration.BROKER_OUT_TOPIC)
        self.Publications = Publications(client=client, subsctiptions=None, history_limit=configuration.HISTORY_LIMIT)
        self.Subscriptions = Subscriptions()

        self.__Subscriptions_set = self.Subscriptions.subscriptions_ids
        self.__Publications_queue = self.Publications.publications_queue
        self.__Router_producer_task_queue = self.Router.Producer.task_queue
        self.__Router_consumer_task_queue = self.Router.Consumer.task_queue

        self.running = False
        # self.Validation = Validation()

    async def update_subscriptions(self, channel_ids: list[int]):
        await self.Subscriptions.update(channel_ids)
        current_subscriptions = self.Subscriptions.subscriptions_ids
        await self.Publications.update_subscriptions(current_subscriptions)

    async def notify_consumer(self):
        await self.Router.notification()
    @property
    def subscriptions_set(self):
        return self.__Subscriptions_set

    @property
    def publications_queue(self):
        return self.__Publications_queue

    @property
    def router_producer_task_queue(self):
        return self.__Router_producer_task_queue

    @property
    def router_consumer_task_queue(self):
        return self.__Router_consumer_task_queue

    async def runloop(self):
        while self.running:
            if not self.__Router_consumer_task_queue.empty():
                try:
                    subscription_task = await self.__Router_consumer_task_queue.get()
                    logger.info("Gathering subscription task from queue with channels: {}", subscription_task.channels_payload)
                    await self.update_subscriptions(subscription_task.channels_payload)
                    logger.info("Done gathering subscription task")
                except Exception as e:
                    logger.exception("Error occurred while gathering subscription task: {}", e)
                finally:
                    self.__Router_consumer_task_queue.task_done()

            if not self.__Router_producer_task_queue.empty():
                try:
                    publication = await self.__Router_producer_task_queue.get()
                    logger.info("Processing publication from channel {}", publication[0])
                    response = Response(
                        time=int(time()),
                        payload={str(publication[0]): str(publication[1])},
                    )

                    await self.Router.send_to_topic(response)
                    logger.info("Publication has been published to broker topic successfully")
                except Exception as e:
                    logger.exception("Error occurred while publishing to broker topic: {}", e)
                finally:
                    self.__Router_producer_task_queue.task_done()

            await asyncio.sleep(0.1)


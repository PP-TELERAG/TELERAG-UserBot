import asyncio
import httpx
from pydantic import BaseModel
from typing import Any
from loguru import logger
class Task(BaseModel):
    user_id: int
    channels_payload: set[int]

class Response(BaseModel):
    time: int
    payload: dict[str, str]

class Consumer:
    def __init__(self, broker_url: str, broker_topic: str):
        self.task_queue = asyncio.Queue()
        self.broker_url = broker_url
        self.broker_topic = broker_topic

        # В агрегаторе будет опрос очереди если в ней что-то появилось

    async def get_by_notification(self):
        async with httpx.AsyncClient() as client:
            try:
                message = await client.get(f"{self.broker_url}/topics/{self.broker_topic}/consume")
                if message.status_code != 200:
                    logger.error("Error occurred while getting message from broker: code: {}", message.status_code)
                data = message.json()
                task = Task(**data)
                await self.task_queue.put(task)
            except Exception as e:
                logger.exception("An exception occurred while getting message from broker: {}", e)

class Producer:
    def __init__(self, broker_url: str, broker_topic: str):
        self.response_queue = asyncio.Queue()
        self.broker_url = broker_url
        self.broker_topic = broker_topic
        self.running = False

    async def produce_message(self, message: Task):
        await self.response_queue.put(message)

    async def __queue_handler(self):
        async with httpx.AsyncClient() as client:
            while self.running:
                message = await self.response_queue.get()
                try:
                    response = await client.post(
                        f"{self.broker_url}/topics/{self.broker_topic}/produce",
                        json=message
                    )
                    if response.status_code != 200:
                        logger.error("Error occurred while sending message to broker: {}", response.status_code)
                except Exception as e:
                    logger.exception("An exception occurred while sending message to broker: {}", e)
                finally:
                    self.response_queue.task_done()

    async def start(self):
        self.running = True
        asyncio.create_task(self.__queue_handler())

    async def stop(self):
        self.running = False
        await self.response_queue.join()


class Router:
    def __init__(self, broker_url: str, broker_in_topic: str, broker_out_topic: str):
        self.Producer = Producer(broker_url, broker_in_topic)
        self.Consumer = Consumer(broker_url, broker_out_topic)

    async def notification(self):
        await self.Consumer.get_by_notification()


    async def send_to_topic(self, message: Response): #Нужна валидация сообщения
        await self.Producer.produce_message(message)

    async def pop_from_queue(self):
        await self.Consumer.task_queue.get()
        self.Consumer.task_queue.task_done()














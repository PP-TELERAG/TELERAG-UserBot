import asyncio
import httpx
from loguru import logger
from src.Models import *
class BrokerGateway:

    def __init__(self, broker_ulr: str, broker_in_topic: str, broker_out_topic: str):
        self.__broker_consume_subscriptions_worker_task_url = f"{broker_ulr}/topics/{broker_in_topic}/consume"
        self.__broker_produce_publications_url = f"{broker_ulr}/topics/{broker_out_topic}/produce"

    async def consume_subscriptions_worker_task(self):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.__broker_consume_subscriptions_worker_task_url)
                if response.status_code != 200:
                    logger.error("Bad response from broker while trying to consume subscription worker task: {}", response.status_code)
                    return

                data = response.json()
                message = data.get("Message", {})
                subject = message.get("subject", "").lower()
                body = message.get("body", {})

                user_id = body.get("userId")
                channels_payload = set()

                payload = body.get("payload", {})
                channels_field = payload.get("channels")

                if channels_field is not None:
                    if isinstance(channels_field, int):
                        channels_payload = {channels_field}
                    elif isinstance(channels_field, list):
                        channels_payload = set(channels_field)
                    else:
                        logger.warning("Unsupported type for channels payload: {}", type(channels_field))
                        return
                else:
                    logger.warning("channels field is missing or empty in message body")
                    return

                if subject is None:
                    logger.error("Task subject was not specified. Skipping...")
                    return

                if subject == "subscribe":
                    request_obj = SubscribeRequest(
                        user_id=user_id,
                        channels_payload=channels_payload
                    )
                elif subject == "unsubscribe":
                    request_obj = UnsubscribeRequest(
                        user_id=user_id,
                        channels_payload=channels_payload
                    )
                else:
                    logger.warning("Unsupported subscriptions task subject: {}. Skipping...", subject)
                    return

                logger.info("Parsed consumed request object: {}", request_obj)
                return request_obj
            except Exception as e:
                logger.exception("Exception while consuming subscription worker task: {}", e)

    async def produce_message_to_broker(self, response):
        if type(response) is not ResponseToRAG or type(response) is not RemoveSourceResponseToRAG:
            logger.warning("Unsupported response type: {}. Skipping...", type(response))
        data = {
            "Message": {
                "method" : "",
                "subject" : "addDoc" if type(response) is not RemoveSourceResponseToRAG else "removeDoc",
                "body" : {
                    "channelId" :  response.channel_id,
                    "payload" : {
                        "text" : response.texts if type(response) is not RemoveSourceResponseToRAG else ""
                    }
                }
            }
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.__broker_produce_publications_url, json=data)
                if response.status_code != 200:
                    logger.error("Failed to produce message to broker: {}", response.status_code)
            except Exception as e:
                logger.exception("Exception while producing message: {}", e)




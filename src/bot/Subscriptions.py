import re
import types
from pyrogram import Client
from pyrogram.errors import PeerIdInvalid
from loguru import logger

class Subscriptions:

    def __init__(self):
        self.subscriptions_ids = set()
        self.client = Client()

    async def __fetch_subscriptions(self):
        async with self.client as session:
            dialogs = await session.get_dialogs()
            self.subscriptions_ids = {dialog.chat.id for dialog in dialogs if dialog.chat.type in ("channel", "supergroup")}

    async def __join_channels(self, channel_ids: list[int]):
        if not self.subscriptions_ids:
            await self.__fetch_subscriptions()

        async with self.client as client:
            for channel_id in channel_ids:
                if channel_id not in self.subscriptions_ids:
                    try:
                        await client.join_chat(channel_id)
                        logger.info("Joined channel {}", channel_id)
                        self.subscriptions_ids.add(channel_id)
                    except Exception as e:
                        logger.exception("Exception occurred while joining channel {}: {}", channel_id, e)
                else:
                    logger.info("Already joined channel {}", channel_id)

    async def __leave_channels(self, channel_ids: list[int]):
        pass

    async def __validate_channel_id(self, channel_id: int):
        async with self.client as client:
            try:
                channel = await client.get_chat(channel_id)
                if channel.type == "supergroup" or channel.type == "channel":
                    logger.info("Channel {} was validated successfully (type {})", channel_id, channel.type)
                    return True
                else:
                    logger.warning("Channel {} has unsupported type: {}", channel_id, channel.type)
                    return False
            except Exception as e:
                logger.exception("Error occurred while validating a channel {}: {}", channel_id, e)

    async def update(self, ids: list[int]):
        temp_ids = []
        for id in ids:
            if await self.__validate_channel_id(id):
                temp_ids.append(id)

        logger.info("IDs to subscribe {}. Joining to {}", temp_ids, len(ids))
        await self.__join_channels(temp_ids)

    async def update_privates(self):
        pass


    async def __send_invite_to_private_channel(self):
        pass




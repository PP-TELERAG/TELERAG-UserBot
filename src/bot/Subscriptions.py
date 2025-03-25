import re
import types
from pyrogram import Client
from pyrogram.errors import PeerIdInvalid


class Subscriptions:

    def __init__(self):
        self.subscriptions_id = set()

    async def __fetch_subscriptions(self, client: Client):
        async with client as session:
            dialogs = await session.get_dialogs()
            self.subscriptions_id = {
                dialog.chat.id for dialog in dialogs if dialog.chat.type in ("channel", "supergroup")}

    async def __join_channels(self, client: Client, channel_ids: list[int]):
        if not self.subscriptions_id:
            await self.__fetch_subscriptions(client)

        async with client:
            for channel_id in channel_ids:
                if channel_id not in self.subscriptions_id:
                    try:
                        await client.join_chat(channel_id)
                        print(f"Joined {channel_id}")
                        self.subscriptions_id.add(channel_id)
                    except Exception as e:
                        print(f"Failed to join {channel_id}")
                else:
                    print(f"Already joined {channel_id}")

    async def __leave_channels(self, client: Client, channel_ids: list[int]):
        pass

    async def __validate_channel_id(self, client: Client, channel_id: int):
        async with client:
            try:
                channel = await client.get_chat(channel_id)
                if channel.type == "supergroup" or channel.type == "channel":
                    return True
                return False
            except PeerIdInvalid as e:
                print(f"Failed to validate {channel_id}")

    async def update(self, client: Client, ids: list[int]):
        temp_ids = []
        for id in ids:
            if self.__validate_channel_id(client, id):
                temp_ids.append(id)

        print(f"IDs to subscribe{temp_ids}. Joining to {len(temp_ids)} IDs")

        await self.__join_channels(client, temp_ids)

    async def update_privates(self):
        pass

    async def __send_invite_to_private_channel(self):
        pass

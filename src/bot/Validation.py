import re
from pyrogram import Client, errors


class Validation:
    def __init__(self, client: Client, channel_identifier: str):
        self.channel_identifier = channel_identifier
        self.client = client
        self.result = {"status": "", "description": "", "channel_id": ""}

    async def validate(self) -> dict:
        invite_match = self.__is_invite_link()
        normal_link_match = self.__is_normal_link()

        if invite_match:
            self.result["status"] = "error"
            self.result["description"] = "Private channels are not supported."
            return self.result

        elif normal_link_match:
            self.channel_identifier = normal_link_match.group(1)

        elif self.__if_channel_id():
            self.channel_identifier = self.__complete_channel_id(
                self.channel_identifier)
            self.result["channel_id"] = self.channel_identifier
            self.result["status"] = "success"
            self.result["description"] = "Channel ID retrieved"
            return self.result

        elif self.__is_username() or self.__is_plain_username():
            pass

        else:
            self.result["status"] = "error"
            self.result["description"] = "Invalid channel identifier."
            return self.result

        async with self.client:
            try:
                chat = await self.client.get_chat(self.channel_identifier)
                self.result["channel_id"] = str(chat.id)
                self.result["status"] = "success"
                self.result["description"] = "Channel ID retrieved"
            except errors.PeerIdInvalid:
                self.result["status"] = "error"
                self.result["description"] = "Invalid channel ID."
            except errors.RPCError as e:
                self.result["status"] = "error"
                self.result["description"] = \
                    f"Error retrieving channel ID: {str(e)}"

        return self.result

    def __is_invite_link(self):
        return re.match(r"https://t\.me/\+(\w+)", self.channel_identifier)

    def __is_normal_link(self):
        return re.match(r"https://t\.me/([\w\d_]+)", self.channel_identifier)

    def __is_username(self):
        return re.match(r"^@[\w\d_]+$", self.channel_identifier)

    def __is_plain_username(self):
        return re.match(r"^[\w\d_]+$", self.channel_identifier)

    def __if_channel_id(self):
        try:
            return int(self.channel_identifier).is_integer()
        except Exception:
            return False

    def __complete_channel_id(self, channel_id: str) -> str:
        if not channel_id.startswith("-100"):
            return f"-100{channel_id}"
        return channel_id

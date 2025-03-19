import re
import types

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
import asyncio

client = Client()

emoji_pattern = re.compile(
"["
    "\U0001F600-\U0001F64F"  # эмодзи: смайлики
    "\U0001F300-\U0001F5FF"  # символы и пиктограммы
    "\U0001F680-\U0001F6FF"  # транспорт и карты
    "\U0001F1E0-\U0001F1FF"  # флаги
    "]+",
    flags=re.UNICODE
)

def remove_emoji(text: str) -> str:
    return emoji_pattern.sub(r"", text)

async def subscribe_to_channels(channel_ids: list[int]):
    dialogs = await client.get_dialogs()

    subscriptions = {dialog.chat.id for dialog in dialogs if dialog.chat.type in ("channel", "supergroup")}

    for channel_id in channel_ids:
        if channel_id not in subscriptions:
            try:
                await client.join_chat(channel_id)
                print(f"Joined {channel_id}")
            except Exception as e:
                print(f"Failed to join {channel_id}")
        else:
            print(f"Already joined {channel_id}")

async def new_publication_handler(message: types.Message):
    if message.chat.type != "channel":
        return

    if message.text:
        clean_text = remove_emoji(message.text)
        print(f"New publication in channel {message.chat.id}: {clean_text}")

    else:
        if message.photo:
            print(f"Publication in channel {message.chat.id} is a photo. Skipping...")
        else:
            print(f"Publication in channel {message.chat.id} does not contain any text. Skipping...")

    



async def main():
    pass


if __name__ == '__main__':
    asyncio.run(main())

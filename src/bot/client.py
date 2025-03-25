from pyrogram import Client

from src.config.config import settings

app = Client(
    name="./account",
    workdir=".",
    api_id=settings.PYRO_API_ID,
    api_hash=settings.PYRO_API_HASH,
    app_version="1.0",
    device_model="TELERAG",
)

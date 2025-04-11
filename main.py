from loguru import logger
from pyrogram import Client, idle
from fastapi import FastAPI, responses

from src import CollectorManager, get_settings

import asyncio
import uvicorn

app = FastAPI()
settings = get_settings()
logger.add("logs/UserBot-Report-Latest.log",
           rotation=settings.LOGGER_ROTATION,
           retention=settings.LOGGER_RETENTION_DAYS,
           encoding=settings.LOGGER_ENCODING,
           level=settings.LOGGER_LOG_LEVEL,
)

async def api_start():
    uvicorn_config = uvicorn.Config(
        app=app,
        port=settings.API_PORT,
        host=settings.API_HOST,
        loop="asyncio",
    )
    server = uvicorn.Server(config=uvicorn_config)
    await server.serve()

async def main():

    client = Client(api_id=settings.PYRO_API_ID, api_hash=settings.PYRO_API_HASH, name="TELERAG USERBOT COLLECTOR")
    await client.start()

    manager = CollectorManager(client=client, settings=settings)
    await manager.stop_routines()

    api_task = asyncio.create_task(api_start())

    await idle()

    api_task.cancel()
    try:
        await api_task
    except asyncio.CancelledError:
        logger.info("FastAPI routine stopped.")

    await manager.stop_routines()
    await client.stop()

    logger.info("Everything is terminated.")

@app.get("/notify")
async def notify():
    manager = CollectorManager.get_instance()
    await manager.consume_by_notification()
    return responses.Response(200)

if __name__ == "__main__":
    asyncio.run(main())

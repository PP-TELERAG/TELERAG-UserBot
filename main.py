from linecache import clearcache
import uvicorn
from loguru import logger

from pyrogram import Client, idle
from fastapi import FastAPI, responses
import asyncio
from src.bot import Agregator
from src.config.config import get_settings
api = FastAPI()
settings = get_settings()
logger.add("logs/collector_depug.log",
           rotation=settings.LOGGER_ROTATION,
           retention=settings.LOGGER_RETENTION,
           encoding=settings.LOGGER_ENCODING,
           level=settings.LOG_LEVEL)
async def api_start():
    uvicorn_config = uvicorn.Config(api, host="0.0.0.0", port=settings.PORT, log_level=settings.LOG_LEVEL, loop="asyncio")
    server = uvicorn.Server(uvicorn_config)
    await server.serve()

async def main():

    client = Client(api_id=settings.PYRO_API_ID, api_hash=settings.PYRO_API_HASH)
    await client.start()

    aggregator = Agregator(configuration=settings, client=client)
    aggregator.Publications.start()

    runloop_task = asyncio.create_task(aggregator.runloop())

    api_task = asyncio.create_task(api_start())

    await idle()

    runloop_task.cancel()
    try:
        await runloop_task
    except asyncio.CancelledError:
        pass

    try:
        await api_task
    except asyncio.CancelledError:
        pass

    await client.stop()

@api.get("/UserBot/Notify")
async def notify():
    agregator = Agregator()
    agregator.Router.notification()
    return responses.Response(status_code=200)

if __name__ == '__main__':
    asyncio.run(main())



import asyncio

from src.bot.client import app


async def main():
    async with app:
        me = await app.get_me()
        print("Вход выполнен\n\n", "Информация о профиле:\n", me)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

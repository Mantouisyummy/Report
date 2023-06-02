import asyncio
from os import getenv
from dotenv import load_dotenv

from disnake import Intents
from disnake.ext.commands import CommandSyncFlags

from core.bot import Bot

def main():

    loop = asyncio.new_event_loop()

    bot = Bot(intents=Intents.all(),command_sync_flags=CommandSyncFlags.default(),loop=loop)

    try:
        load_dotenv()
        bot.run(getenv("TOKEN"))
    except KeyboardInterrupt:
        asyncio.get_event_loop().close()

if __name__ == "__main__":
    main()
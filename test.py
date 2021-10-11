import asyncio
import os
import utils

import telethon
from telethon import TelegramClient as tgclient

async def main():
    print(utils.get_path_ext('1.webp'))




asyncio.get_event_loop().run_until_complete(main())
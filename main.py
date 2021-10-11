import asyncio
import os

import telethon
from telethon import TelegramClient as tgclient
import telethon.tl.types

import cache
import stickers
from stickers import TgStickerPack
import tgapi
from auth import SignInState
import gvars
import auth


async def main():
    await gvars.client.connect()
    gvars.state = SignInState.CONNECTED_NSI
    await auth.signin_cli()
    sn: str = "Ausmotes"
    await stickers.get_pack(sn, force_download_stickers=True)
    print('Done!')


asyncio.get_event_loop().run_until_complete(main())

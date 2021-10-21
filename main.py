import asyncio
import os

import telethon
from telethon import TelegramClient as tgclient
import telethon.tl.types as tg
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
    loc: tg.TypeInputFile = await tgapi.upload_file(gvars.DATAPATH + 'fbm.png')
    await tgapi.send_sb(loc)


asyncio.get_event_loop().run_until_complete(main())

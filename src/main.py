import asyncio

import telethon.tl.types as tg
from src.Tg.auth import SignInState
from src import gvars
from src.Tg import auth, tgapi


async def main():
    await gvars.client.connect()
    gvars.state = SignInState.CONNECTED_NSI
    await auth.signin_cli()
    loc: tg.TypeInputFile = await tgapi.upload_file(gvars.DATAPATH + 'fbm.png')
    await tgapi.send_sb(loc)


asyncio.get_event_loop().run_until_complete(main())

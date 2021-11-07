import asyncio
import sys

import telethon.tl.types as tg

from src.Tg.auth import SignInState
from src import gvars
from src.Qt import gui
from src.Tg import auth, tgapi


async def master():
    # print('coroutine started')
    # await gvars.client.connect()
    # gvars.state = SignInState.CONNECTED_NSI
    # print(gvars.client.is_connected())
    # print('urmom')
    # await auth.signin_cli()
    # loc: tg.TypeInputFile = await tgapi.upload_file(gvars.DATAPATH + 'fbm.png')
    # await tgapi.send_sb(loc)
    gui.main()
    await asyncio.Future()


# async def main():
#     await gvars.client.connect()
#     gvars.state = SignInState.CONNECTED_NSI
#     await auth.signin_cli()
#     print(await tgapi.get_owned_stickerset_shortnames())

def main():
    gui.main()


if __name__ == '__main__':
    main()


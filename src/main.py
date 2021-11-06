import asyncio
import sys

import qasync
import telethon.tl.types as tg
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop
from asyncio.events import AbstractEventLoop

from src.Tg.auth import SignInState
from src import gvars
from src.Qt import gui
from src.Tg import auth, tgapi


async def master():
    print('coroutine started')
    await gvars.client.connect()
    gvars.state = SignInState.CONNECTED_NSI
    print(gvars.client.is_connected())
    print('urmom')
    # await auth.signin_cli()
    # loc: tg.TypeInputFile = await tgapi.upload_file(gvars.DATAPATH + 'fbm.png')
    # await tgapi.send_sb(loc)
    gui.main()


async def main():
    await gvars.client.connect()
    gvars.state = SignInState.CONNECTED_NSI
    await auth.signin_cli()
    print(await tgapi.get_owned_stickerset_shortnames())




if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

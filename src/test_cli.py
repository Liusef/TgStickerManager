import asyncio

from src.Tg import auth, tgapi


async def main():
    await auth.signin_cli()
    packs = await tgapi.get_owned_stickerset_shortnames()
    print('\nUser owns the following packs:\n' + str(packs))

    
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
import os

from telethon import TelegramClient as tgclient

from src import apikeys, utils
from src.Tg.auth import SignInState

# API Keys for Telegram Application
# apikeys.py not added to this repository for safety
api_id: int = apikeys.api_id
api_hash: str = apikeys.api_hash

# Paths
DATAPATH: str = 'tgsticker' + os.sep  # Root program data path
SESSIONPATH: str = DATAPATH + 'sessions' + os.sep  # Login session path
CACHEPATH: str = DATAPATH + 'cache' + os.sep # Data Caching Path
utils.check_all_paths([DATAPATH, SESSIONPATH, CACHEPATH])  # Checking if all paths exist

# MIME Types
MIME: dict[str, str] = {
    'image/webp' : 'webp',
    'application/x-tgsticker' : 'tgs',
    'text/plain' : 'txt',
    'application/octet-stream' : ''
}

# User handles
STICKERBOT: str = 'Stickers'  # Sticker bot   : @Stickers

# Telegram client object to make requests and receive data
def get_client(name: str) -> tgclient:
    return tgclient(SESSIONPATH + name, api_id, api_hash)
client: tgclient = get_client('user')

# SignInState object to track the state of the telegram client
state: SignInState = SignInState.NULL

# Bot Commands
SB_NEW: str = '/newpack'  # New Sticker Pack
SB_NEW_ANIMATED: str = '/newanimated'  # New Sticker Pack (Animated)
SB_ADD: str = '/addsticker'  # Add Sticker To Existing Pack
SB_EDIT: str = '/editsticker'  # Edit Emojis Associated with Sticker
SB_ORDER: str = '/ordersticker'  # Change Position of a Sticker in the Pack
SB_SETICON: str = '/setpackicon'  # Change Icon of a Sticker Pack
SB_DELETE: str = '/delsticker'  # Delete a Sticker in a Sticker Pack
SB_CANCEL: str = '/cancel'  # Cancels existing operations

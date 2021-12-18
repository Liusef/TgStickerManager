import os

import logging
from telethon import TelegramClient as tgclient

from src import apikeys, utils
from src.Tg.auth import SignInState


# API Keys for Telegram Application
# apikeys.py not added to this repository for safety
api_id: int = apikeys.api_id
api_hash: str = apikeys.api_hash

# Constants
CURRENT_USER: str = 'user'
PACKS_FNAME: str = 'packs.json'

# Paths
DATAPATH: str = 'tgsticker' + os.sep  # Root program data path
USERSPATH: str = DATAPATH + 'users' + os.sep  # Login session path
CACHEPATH: str = DATAPATH + 'cache' + os.sep  # Data Caching Path

# Logging
utils.setup_logging(
    level=logging.DEBUG,
    console=True,
    file=True,
    path='debug.log'
)

utils.check_all_paths([DATAPATH, USERSPATH, CACHEPATH])  # Checking if all paths exist

# MIME Types
MIME: dict[str, str] = {
    'image/webp': 'webp',
    'application/x-tgsticker': 'tgs',
    'text/plain': 'txt',
    'application/octet-stream': ''
}

# User handles
STICKERBOT: str = 'Stickers'  # Sticker bot   : @Stickers


# Helper methods to get paths without long string concatenation garbage
def get_user_path(name: str) -> str:
    """
    Gets the path on the system to the folder with the specified user's session and owned packs
    :param name: The name of the user locally (not the same as the telegram username, as of now it is always "user"
    :return: The path on the system of where all the user's information is saved on the system
    """
    return utils.check_path(USERSPATH + name + os.sep)


def get_current_user_path() -> str:
    """
    Gets the path on the system of the currently signed in user.
    The current user is determined by checking the CURRENT_USER constant variable
    :return: The path on the system of where all the current user's information is saved on the system
    """
    return get_user_path(CURRENT_USER)


# Telegram client object to make requests and receive data
def get_client(name: str) -> tgclient:
    """
    Creates the TelegramClient object of the specified user on the system. If the specified user does not exist,
    the program will create a new directory for the user. Multiple users is not supported so the value that should be
    used is "user"
    :param name: The username of the local user to sign in as. Currently defaults to "user"
    :return: The TelegramClient object of the specified local user
    """
    return tgclient(get_user_path(name) + name, api_id, api_hash)


client: tgclient = get_client(CURRENT_USER)

# SignInState object to track the state of the telegram client
state: SignInState = SignInState.NULL

# Bot Commands
SB_NEW: str = '/newpack'                # New Sticker Pack
SB_NEW_ANIMATED: str = '/newanimated'   # New Sticker Pack (Animated)
SB_ADD: str = '/addsticker'             # Add Sticker To Existing Pack
SB_EDIT: str = '/editsticker'           # Edit Emojis Associated with Sticker
SB_ORDER: str = '/ordersticker'         # Change Position of a Sticker in the Pack
SB_SETICON: str = '/setpackicon'        # Change Icon of a Sticker Pack
SB_DELETE: str = '/delsticker'          # Delete a Sticker in a Sticker Pack
SB_CANCEL: str = '/cancel'              # Cancels existing operations

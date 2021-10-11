from enum import Enum


class SignInState(Enum):
    """
    Denotes the current state of the program in the sign in process, only SIGNED_IN will allow you to make API Calls

    0 - NULL          : Program not initialized

    1 - CONNECTED_NSI : Program connected to Telegram API, User not signed in

    2 - SIGNED_IN     : Program connected and signed in, you're ready to go! ✨

    3 - AWAITING_CODE : Program sent sign in request to telegram, waiting for user to enter sign in code

    4 - AWAITING_2FA  : Program sent sign in request to telegram, waiting for user to enter 2fa password

    5 - FLOOD_WAIT_ERR: Too many sign in requests submitted, wait (usually 24 hours)
    """
    NULL = 0
    CONNECTED_NSI = 1
    SIGNED_IN = 2
    AWAITING_CODE = 3
    AWAITING_2FA = 4
    FLOOD_WAIT_ERR = 5


import telethon
from telethon import TelegramClient as tgclient
from telethon.errors import FloodWaitError
from telethon.errors import SessionPasswordNeededError
from telethon.errors import PhoneCodeInvalidError
import gvars
import utils


async def signin_cli():
    """
    Facilitates the Sign in process to telegram, uses SignInState to keep track of process.
    For use with Command Line Interfaces only.

    :return: None
    """
    if await gvars.client.is_user_authorized():  # Checking if the user is Signed in (2)
        print("You're all signed in and ready to go! No need to sign in again :]")
        gvars.state = SignInState.SIGNED_IN
        return  # Exits if Signin state is 2 - SIGNED_IN

    next_input: str = input("Phone number: ")  # Reading phone number from the user (login id)
    await signin_handler_phone(next_input)  # Pass input to relevant handler
    if gvars.state == SignInState.SIGNED_IN:
        print("Successfully Signed in!")
        return  # Exits if Signin state is 2 - SIGNED_IN
    if gvars.state != SignInState.AWAITING_CODE:
        raise Exception("signin_cli expected state SIGNED_IN or AWAITING_CODE")

    next_input = input("Code: ")  # User enters code they received from @Telegram
    await signin_handler_code(next_input)  # Pass input to relevant handler
    if gvars.state == SignInState.SIGNED_IN:
        print("Successfully Signed in!")
        return  # Exits if Signin state is 2 - SIGNED_IN
    if gvars.state != SignInState.AWAITING_2FA:
        raise Exception("Signin_cli expected state SIGNED_IN or AWAITING_2FA")

    next_input = input("2fa password: ")  # Users enters their 2FA password
    await signin_handler_2fa(next_input)  # Pass input to relevant handler
    if gvars.state == SignInState.SIGNED_IN:
        print("Successfully Signed in!")
        return  # Exits if Signin state is 2 - SIGNED_IN

    raise Exception("Signin_cli expected state SIGNED_IN or AWAITING_2FA")
    # If signin is not completed by this point in the signin process, exception is thrown as what the fuck


async def signin_handler_phone(phone: str):
    """
    Sends sign in request to telegram using phone number

    :param phone: The phone number of the user that wants to sign in, must include country code
    :return: None
    """
    try:
        var = await gvars.client.sign_in(phone)
        print(var.stringify())
        if type(var) == telethon.types.auth.SentCode:
            gvars.state = SignInState.AWAITING_CODE
        elif await gvars.client.is_user_authorized():
            gvars.state = SignInState.SIGNED_IN
        else:
            utils.raise_exception_no_err(var)
    except FloodWaitError:
        gvars.state = SignInState.FLOOD_WAIT_ERR


async def signin_handler_code(verif: str):
    """
    Sends sign in request to telegram using the signin verification code

    :param verif: The verification code sent to the user via @Telegram
    :return: None
    """
    try:
        var = await gvars.client.sign_in(code=verif)
        print(var.stringify())
        if await gvars.client.is_user_authorized():
            gvars.state = SignInState.SIGNED_IN
        elif type(var) != telethon.types.User:
            raise Exception("Program called sign_in after received code, method did not return type User. " +
                            "Program raised exception because sign in failed, or other error")
        else:
            utils.raise_exception_no_err(var)
    except PhoneCodeInvalidError:
        print("PhoneCodeInvalidError, wot")
        gvars.state = SignInState.AWAITING_CODE
    except SessionPasswordNeededError:
        gvars.state = SignInState.AWAITING_2FA


async def signin_handler_2fa(tfa: str):
    """
    Sends sign in request to telegram using 2FA password

    :param tfa: The 2 factor auth password
    :return: None
    """
    var = await gvars.client.sign_in(password=tfa)
    print(var.stringify())
    if await gvars.client.is_user_authorized():
        gvars.state = SignInState.SIGNED_IN
    elif type(var) != telethon.types.User:
        raise Exception("Program called sign_in after received code, method did not return type User. " +
                        "Program raised exception because sign in failed, or other error")
    else:
        utils.raise_exception_no_err(var)


async def signin_handler_request_new_code(phone: str):
    """
    Requests a new sign in verification code

    :param phone: The phone number of the user, must include country code
    :return: None
    """
    var = await gvars.client.send_code_request(phone)
    print(var.stringify())

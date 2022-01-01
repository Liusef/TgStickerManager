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
from telethon.errors import FloodWaitError
from telethon.errors import SessionPasswordNeededError
from telethon.errors import PhoneCodeInvalidError
import logging
from logging import debug, info, warning, error, critical
from src import gvars, utils


async def signin_cli():
    """
    Facilitates the Sign in process to telegram, uses SignInState to keep track of process.
    For use with Command Line Interfaces only.

    :return: None
    """
    warning('This method does not have proper logging implemented')

    await ensure_connected()

    if await gvars.client.is_user_authorized():  # Checking if the user is Signed in (2)
        info("You're all signed in and ready to go! No need to sign in again :]")
        gvars.state = SignInState.SIGNED_IN
        return  # Exits if Signin state is 2 - SIGNED_IN

    phone: str = input("Phone number: ")  # Reading phone number from the user (login id)
    await signin_handler_phone(phone)  # Pass input to relevant handler
    if gvars.state == SignInState.SIGNED_IN:
        info("Successfully Signed in!")
        return  # Exits if Signin state is 2 - SIGNED_IN
    if gvars.state != SignInState.AWAITING_CODE:
        raise Exception("signin_cli expected state SIGNED_IN or AWAITING_CODE")

    code = input("Code: ")  # User enters code they received from @Telegram
    await signin_handler_code(phone, code)  # Pass input to relevant handler
    if gvars.state == SignInState.SIGNED_IN:
        info("Successfully Signed in!")
        return  # Exits if Signin state is 2 - SIGNED_IN
    if gvars.state != SignInState.AWAITING_2FA:
        raise Exception("Signin_cli expected state SIGNED_IN or AWAITING_2FA")

    tfa = input("2fa password: ")  # Users enters their 2FA password
    await signin_handler_2fa(tfa)  # Pass input to relevant handler
    if gvars.state == SignInState.SIGNED_IN:
        info("Successfully Signed in!")
        return  # Exits if Signin state is 2 - SIGNED_IN

    raise Exception("Signin_cli expected state SIGNED_IN or AWAITING_2FA")
    # If signin is not completed by this point in the signin process, exception is thrown as what the fuck


async def ensure_connected():
    """
    Ensures that the TelegramClient is connected to telegram
    :return: None
    """
    info('Ensuring that client is connected to Telegram')
    await gvars.client.connect()
    gvars.state = SignInState.CONNECTED_NSI


async def signin_handler_phone(phone: str):
    """
    Sends sign in request to telegram using phone number

    :param phone: The phone number of the user that wants to sign in, must include country code
    :return: None
    """

    debug('src.Tg.auth.signin_handler_phone() called')
    debug(f'phone: {phone}')
    info('Attempting authentication with phone number')
    try:
        debug(f'creating tgclient.sign_in coroutine and adding to the event loop')
        var = await gvars.client.sign_in(phone)
        debug(f'tgclient.sign_in coroutine finished and returned a value:\n{var.stringify()}')
        if type(var) == telethon.types.auth.SentCode: awaiting_code()
        elif await gvars.client.is_user_authorized(): signed_in()
        else: unexpected(var)
    except FloodWaitError as e: flood_wait(e)


async def signin_handler_code(phone: str, verif: str):

    """
    Sends sign in request to telegram using the signin verification code
    :param phone: The phone number of the user to sign in to
    :param verif: The verification code sent to the user via @Telegram
    :return: None
    """
    debug('src.Tg.auth.signin_handler_phone() called')
    debug(f'phone: {phone}')
    debug(f'code:  {verif}')
    info('Attempting authentication with phone number and code')
    try:
        debug(f'creating tgclient.sign_in coroutine and adding to the event loop')
        var = await gvars.client.sign_in(phone=phone, code=verif)
        debug(f'tgclient.sign_in coroutine finished and returned a value:\n{var.stringify()}')
        if await gvars.client.is_user_authorized(): signed_in()
        else: unexpected(var)
    except PhoneCodeInvalidError:
        error(f'The phone code entered ({verif}) was invalid. Sign in unsuccessful')
        gvars.state = SignInState.AWAITING_CODE
        debug('SignInState set to AWAITING_CODE')
    except SessionPasswordNeededError:
        info('User needs Two Factor Authentication Password to Sign In')
        gvars.state = SignInState.AWAITING_2FA
        # TODO Implement 2FA and make sure you remove this after you do (and add a warning saying it may not work)
        critical('Two Factor Sign in not implemented, program must halt')
        raise NotImplementedError('User account needs 2nd factor to sign in. 2FA is not implemented in the GUI.')


async def signin_handler_2fa(tfa: str):
    """
    Sends sign in request to telegram using 2FA password

    :param tfa: The 2 factor auth password
    :return: None
    """
    debug('src.Tg.auth.signin_handler_2fa() called')
    debug(f'2fa: {tfa}')
    warning('This method has not been tested and may not work properly, proceed with caution.')
    warning('This method does not have proper logging implemented')
    var = await gvars.client.sign_in(password=tfa)
    print(var.stringify())
    if await gvars.client.is_user_authorized(): signed_in()
    else: unexpected(var)


async def signin_handler_request_new_code(phone: str):
    """
    Requests a new sign in verification code

    :param phone: The phone number of the user, must include country code
    :return: None
    """
    info('Sending Request to telegram for sign in code')
    warning('This method does not generate a new code for sign in. If needed, use the last sign in code given to you')
    debug('creating tgclient.send_code_request coroutine and adding to the event loop')
    var = await gvars.client.send_code_request(phone)
    debug(f'Received response from tgclient.send_code_request:\n{var.stringify()}')


def awaiting_code():
    """
    Sets the state to SignInState.AWAITING_CODE
    :return: None
    """
    info('tgclient.sign_in needs a code to continue: verification code sent to your telegram account')
    debug('SignInState set to AWAITING_CODE')
    gvars.state = SignInState.AWAITING_CODE


def signed_in():
    """
    Sets the state to SignInState.SIGNED_IN
    :return: None
    """
    info('tgclient.sign_in was successful. User is now authorized to make Telegram API calls!')
    gvars.state = SignInState.SIGNED_IN
    debug('SignInState set to SIGNED_IN')


def flood_wait(e: BaseException):
    """
    Sets the state to SignInState.FLOOD_WAIT_ERR
    :return: None
    """
    error('tgclient.sign_in threw a FloodWaitError. This could mean that too many requests were sent')
    error(f'{str(e)}')
    gvars.state = SignInState.FLOOD_WAIT_ERR


def unexpected(var):
    """
    Call this method when the program hits an unexpected signin state
    :param var: The returned value from Telegram
    :return: None
    """
    critical('tgclient.sign_in returned an unexpected value and the program is unable to continue')
    utils.raise_exception_no_err(var)

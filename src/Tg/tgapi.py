import asyncio
import copy
import os
from typing import Union

from logging import debug, info, warning, error, critical
from telethon.tl.types import Document, InputDocumentFileLocation, InputStickerSetShortName, TypeInputFile, Message, \
    ReplyKeyboardHide
from telethon.tl.types.messages import StickerSet
from telethon.tl.functions.messages import GetStickerSetRequest

from src import gvars, utils


class DocName:
    """
    A class representing the name of a Telegram Document
    """
    def __init__(self, fname: str, mime: str):
        """
        Instantiates a DocName object
        :param fname: The filename of the file
        :param mime: The MIME type of the file
        """
        debug(f'Creating DocName object with fname:{fname} and mime:{mime}')
        self.fname: str = fname if fname is not None else ""
        self.mime: str = mime if mime is not None else ""

    def ext(self) -> str:
        """
        Gets the file extension associated with the file. If a MIME type is present, it retrieves this from a MIME type
        table. Else, it attempts to get the extension from the filename itself. Otherwise it omits the extension
        :return: The extension of the file as a string
        """
        idx: int = self.mime.find('/') + 1
        if (len(self.mime) > 0) and ((m := gvars.MIME.get(self.mime, self.mime[idx:])) != ''):
            return m
        return utils.get_path_ext(self.fname, '')

    def filename(self) -> str:
        """
        Returns the name of the file excluding the extension
        :return: the name of the file excluding the extension
        """
        idx: int = self.fname.find('.')
        return self.fname[0:idx if idx != -1 else len(self.fname)]


def derive_docname(doc: Document) -> DocName:
    """
    Generates a DocName object
    :param doc:
    :return:
    """
    return DocName(utils.get_attr_filename(doc, ""), doc.mime_type)


async def send_sb(inpt: Union[str, Document, TypeInputFile]) -> Message:
    """
    Sends whatever is input to Sticker bot
    :param inpt: The input to send to Sticker bot
    :return: The Message file that Telegram returns
    """
    if isinstance(inpt, str):
        info('Sending message to stickerbot')
        debug(f'message: {inpt}')
        return await gvars.client.send_message(entity=gvars.STICKERBOT, message=inpt)
    else:
        info('Sending file to stickerbot')
        debug(f'file id: {inpt.id}')
        return await gvars.client.send_file(entity=gvars.STICKERBOT, file=inpt, force_document=True)


async def upload_file(path: str) -> TypeInputFile:
    """
    Uploads a file to Telegram but does not send it.
    :param path: The path of the file on the local system
    :return: The Input Location of the file on Telegram's servers
    """
    if not os.path.exists(path):
        critical(f'Could not find file at {path}, program cannot continue')
        raise Exception("File does not exist")
    info(f'Uploading file from {path}')
    return await gvars.client.upload_file(path)


async def upload_callback(sent_bytes: int, total_bytes: int):
    # TODO: Write Method
    # TODO: Write Docstring
    print(str(sent_bytes) + ' / ' + str(total_bytes))


async def await_next_msg_id(current_id: int, user: str, delay: float = 0.1) -> Message:
    """
    Waits for the next message and then continues
    :param current_id: The ID of the current message
    :param user: The name (not nickname) of the chat you want to search
    :param delay: The amount of time to wait between checking (seconds)
    :return: The new message received
    """
    while True:
        msg: Message = await gvars.client.iter_messages(entity=user).__anext__()
        if msg.id != current_id: return msg
        debug(f"Target message not found. Waiting for {delay} seconds...")
        await asyncio.sleep(delay)


async def await_next_msg_str(target_str: str, user: str, delay: float = 0.1) -> Message:
    """
    Waits for a message to show with certain message contents
    :param target_str: The target message contents to search for
    :param user: The name (not nickname) of the chat you want to search
    :param delay: The amount of time to wait between checking (seconds)
    :return: The new message received
    """
    while True:
        msg: Message = await gvars.client.iter_messages(entity=user).__anext__()
        if msg.message == target_str: return msg
        debug(f"Target message not found. Waiting for {delay} seconds...")
        await asyncio.sleep(delay)


def get_document_loc(doc: Document) -> InputDocumentFileLocation:
    """
    Gets the Location object of a Document

    :param doc: The document object in question
    :return: Location object of the input document
    """
    return InputDocumentFileLocation(
        id=doc.id,
        access_hash=doc.access_hash,
        file_reference=doc.file_reference,
        thumb_size='0'
    )


async def download_doc(doc: InputDocumentFileLocation,  meta: DocName, path: str, fname_is_id: bool):
    """
    Downloads a Telegram document to the local device
    :param doc: The File location on Telegram's servers
    :param meta: The DocName metadata
    :param path: The folder on the local device to save to
    :param fname_is_id: Whether or not to set the local filename to the document id
    :return: None
    """
    filename: str = str(doc.id) if fname_is_id else meta.filename()
    info(f'Downloading Telegram document with id: {doc.id} to path: {path}{filename}.{meta.ext()}')
    await asyncio.create_task(gvars.client.download_file(doc, utils.check_path(path) + filename + '.' + meta.ext()))


async def download_doc_nloc(doc: Document, path: str, fname_is_id: bool):
    """
    Downloads a Telegram document to the local device using a Telegram Document object instead of Location
    :param doc: The Telegram Document to download
    :param path: The path on the local system to download to
    :param fname_is_id: Whether or not to set the local filename to the document id
    :return: None
    """
    await download_doc(
        get_document_loc(doc),
        derive_docname(doc),
        path,
        fname_is_id
    )


# TODO Restrict number of concurrent downloads
async def download_doclist(doc_arr: list[InputDocumentFileLocation], meta_arr: list[DocName],
                           path: str, fname_is_id: bool):
    """
    Downloads a list of Documents to the local device
    :param doc_arr: The list of File Locations on Telegram's Servers
    :param meta_arr: A list of DocName metadata corresponding to the File Locations in doc_arr
    :param path: The path on the local system to download to
    :param fname_is_id: Whether or not to set the local filename to the document id
    :return: None
    """
    tasklst: list[asyncio.Task] = []
    utils.check_path(path)

    for i in range(0, len(doc_arr)):
        tsk: asyncio.Task = asyncio.create_task(download_doc(doc_arr[i], meta_arr[i], path, fname_is_id))
        debug("Began download document " + str(i) + '\n' + str(doc_arr[i].id))
        tasklst.append(tsk)

    j: int = 0
    for t in tasklst:
        await t
        j += 1


async def download_doclist_nloc(doc_arr: list[Document], path: str, fname_is_id: bool):
    """
    Downloads a list of Documents to the local device without using the File Locations
    :param doc_arr: The list of Documents to download
    :param path: The path on the local system to download to
    :param fname_is_id: Whether or not to set the local file to the document id
    :return: None
    """
    await download_doclist([get_document_loc(d) for d in doc_arr], [derive_docname(d) for d in doc_arr],
                           path, fname_is_id)


async def get_stickerset(short: str) -> StickerSet:
    """
    Gets a Stickerset (Sticker Pack) object based on the pack's shortname (URL Name)

    :param short: The shortname of the stickerset
    :return: The requested stickerset
    """
    info(f'Getting stickerset with shortname: {short}')
    query: InputStickerSetShortName = InputStickerSetShortName(short_name=short)
    return await gvars.client(GetStickerSetRequest(query))


# This method is super sketchy and might not work if you have a lot of packs but idk how to do it better oops
async def get_owned_stickerset_shortnames() -> list[str]:
    """
    Gets a list of all the sticker packs that the user owns.

    Works by messaging @Stickers to add a sticker to a pack and looking at the reply keyboard that the bot returns
    :return: A list of strings that contains the shortnames of all the packs
    """
    delay: float = 0.1
    info('Checking what stickersets are owned by the current user')
    debug(f'running src.Tg.tgapi.get_owned_stickerset_shortnames with delay {delay}')
    cmsg = await send_sb("/cancel")
    await await_next_msg_id(cmsg.id, gvars.STICKERBOT)
    cmsg = await send_sb("/addsticker")
    # TODO add logs
    msg: Message = await await_next_msg_id(cmsg.id, gvars.STICKERBOT)
    sets: list[str] = []
    print(msg.stringify())
    if msg.reply_markup is None or isinstance(msg.reply_markup, ReplyKeyboardHide) \
            or msg.reply_markup.rows is None or len(msg.reply_markup.rows) == 0:
        return sets
    for r in msg.reply_markup.rows:
        for b in r.buttons:
            sets.append(b.text)
    await send_sb("/cancel")
    return sets

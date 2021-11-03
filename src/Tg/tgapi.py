import asyncio
import os
from typing import Union

from telethon.tl.types import Document, InputDocumentFileLocation, InputStickerSetShortName, TypeInputFile
from telethon.tl.types.messages import StickerSet
from telethon.tl.functions.messages import GetStickerSetRequest

from src import gvars, utils


class DocName:
    # TODO Docstrings
    def __init__(self, fname: str, mime: str):
        self.fname: str = fname if fname is not None else ""
        self.mime: str = mime if mime is not None else ""

    def ext(self) -> str:
        idx: int = self.mime.find('/') + 1
        if (len(self.mime) > 0) and ((m := gvars.MIME.get(self.mime, self.mime[idx:])) != ''):
            return m
        return utils.get_path_ext(self.fname, '')

    def filename(self) -> str:
        idx: int = self.fname.find('.')
        return self.fname[0:idx if idx != -1 else len(self.fname)]


def derive_docname(doc: Document) -> DocName:
    # TODO Docstring
    return DocName(utils.get_attr_filename(doc, ""), doc.mime_type)


async def send_sb(inpt: Union[str, Document, TypeInputFile]):
    # TODO Docstring
    if isinstance(inpt, str):
        await gvars.client.send_message(entity=gvars.STICKERBOT, message=inpt)
    else:
        await gvars.client.send_file(entity=gvars.STICKERBOT, file=inpt, force_document=True)


async def upload_file(path: str) -> TypeInputFile:
    # TODO Docstring
    if not os.path.exists(path):
        raise Exception("File does not exist")
    return await gvars.client.upload_file(path)


async def upload_callback(sent_bytes: int, total_bytes: int):
    # TODO: Write Method
    # TODO: Write Docstring
    print(str(sent_bytes) + ' / ' + str(total_bytes))


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
    # TODO Docstring
    filename: str = str(doc.id) if fname_is_id else meta.filename()
    ext: str = meta.ext()
    ext = ('.' + ext) if (len(ext) > 0) else ext
    await asyncio.create_task(gvars.client.download_file(doc, utils.check_path(path) + filename + '.' + meta.ext()))


async def download_doc_nloc(doc: Document, path: str, fname_is_id: bool):
    # TODO Docstring
    await download_doc(
        get_document_loc(doc),
        DocName(utils.get_attr_filename(doc), doc.mime_type),
        path,
        fname_is_id
    )


# TODO Restrict number of concurrent downloads
async def download_doclist(doc_arr: list[InputDocumentFileLocation], meta_arr: list[DocName],
                           path: str, fname_is_id: bool):
    # TODO Docstring
    tasklst: list[asyncio.Task] = []
    utils.check_path(path)

    for i in range(0, len(doc_arr)):
        tsk: asyncio.Task = asyncio.create_task(download_doc(doc_arr[i], meta_arr[i], path, fname_is_id))
        print("Began download document " + str(i) + '\n' + str(doc_arr[i].id))
        tasklst.append(tsk)

    j: int = 0
    for t in tasklst:
        await t
        print("Finished downloading document " + str(j) + "\n")
        j += 1


async def download_doclist_nloc(doc_arr: list[Document], path: str, fname_is_id: bool):
    # TODO Docstring
    await download_doclist([get_document_loc(d) for d in doc_arr], [derive_docname(d) for d in doc_arr],
                           path, fname_is_id)


async def get_stickerset(short: str) -> StickerSet:
    """
    Gets a Stickerset (Sticker Pack) object based on the pack's shortname (URL Name)

    :param short: The shortname of the stickerset
    :return: The requested stickerset
    """
    query: InputStickerSetShortName = InputStickerSetShortName(short_name=short)
    return await gvars.client(GetStickerSetRequest(query))

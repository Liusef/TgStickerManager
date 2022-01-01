import os
from typing import Union

from telethon.tl.types import Document, DocumentAttributeImageSize, StickerSet, StickerPack, \
    DocumentAttributeFilename, InputDocumentFileLocation, InputStickerSetThumb, InputStickerSetShortName, PhotoSize
from telethon.tl.types.messages import StickerSet as ParentSet
from logging import debug, info, warning, error, critical
from src import gvars, utils
from src.Tg import tgapi
import jsonpickle


class TgSticker:
    """
    A Telegram Sticker (Does not include sticker data)
    """
    def __init__(self, doc: Document, emojis: str, parent_sn: str):
        """
        Instantiates a TgSticker Object
        :param doc: The sticker document from Telegram
        :param emojis: The emojis associated with this sticker
        :param parent_sn: The shortname of the sticker pack this sticker belongs to
        """
        debug(f'Instantiating TgSticker Object under stickerset {parent_sn}')
        self.doc_id: int = doc.id
        self.doc_access_hash: int = doc.access_hash
        self.doc_mimetype: str = doc.mime_type
        self.doc_dc_id: int = doc.dc_id
        self.doc_fileref: bytes = doc.file_reference
        self.filesize: int = doc.size
        self.filename: str = utils.get_doc_attr(doc, DocumentAttributeFilename).file_name
        self.parent_sn: str = parent_sn
        imgsize: DocumentAttributeImageSize = utils.get_doc_attr(doc, DocumentAttributeImageSize)
        self.height: int = imgsize.h
        self.width: int = imgsize.w
        self.emojis: str = emojis

    def get_loc(self) -> InputDocumentFileLocation:
        """
        Gets the InputDocumentFileLocation of the sticker image
        :return: The InputDocumentFileLocation of the sticker image from telegram
        """
        return InputDocumentFileLocation(
            self.doc_id,
            self.doc_access_hash,
            self.doc_fileref,
            '0'
        )

    def get_file_path(self) -> str | None:
        """
        Gets the local file path of the sticker image on the system.
        :return: The string file path of the sticker image. If not found, returns None
        """
        path: str = gvars.CACHEPATH + self.parent_sn + os.sep + str(self.doc_id)
        print(path)
        if os.path.exists(path + '.webp'): return path + '.webp'
        elif os.path.exists(path + '.tgs'): return path + '.tgs'
        else: return None


class TgPackThumb:
    """
    A Telegram Sticker Pack Thumbnail
    """
    def __init__(self, parent_sn: str, height: int, width: int, size: int, dc_id: int, version: int):
        """
        Instantiates a TgPackThumb object
        :param parent_sn: The shortname of the pack this thumbnail belongs to
        :param height: The height of the thumbnail
        :param width: The width of the thumbnail
        :param size: The size of the thumbnail (file size i think?)
        :param dc_id: The DC_ID of the thumbnail
        :param version: The Version of the thumbnail
        """
        debug(f'TgPackThumb object for set {parent_sn} instantiated')
        self.parent_sn: str = parent_sn
        self.height: int = height
        self.width: int = width
        self.size: int = size
        self.dc_id: int = dc_id
        self.version: int = version

    def get_loc(self) -> InputStickerSetThumb:
        """
        Gets the InputLocation of the telegram thumbnail
        :return:
        """
        return InputStickerSetThumb(InputStickerSetShortName(self.parent_sn), self.version)


class TgStickerPack:
    """
    A Telegram Sticker Pack
    """
    def __init__(self, sset: StickerSet, stickers: list[TgSticker], thumb: Union[TgPackThumb, None]):
        """
        Instantiates a TgStickerPack object
        :param sset: The stickerset object from Telegram
        :param stickers: A list of TgSticker objects that belong to this Sticker Pack
        :param thumb: The thumbnail of this sticker pack
        """
        debug(f'TgStickerPack object for set {sset.short_name} instantiated')
        self.id: int = sset.id
        self.access_hash: int = sset.access_hash
        self.name: str = sset.title
        self.sn: str = sset.short_name
        self.size: int = sset.count
        self.hash: int = sset.hash
        self.is_animated: bool = sset.animated
        self.thumb: TgPackThumb = thumb
        self.stickers: list[TgSticker] = stickers

    async def download_stickers(self):
        """
        Downloads all the stickers in this stickerpack to the cache folder associated with this object
        :return:
        """
        info(f'Downloading all stickers in pack {self.sn} to cache')
        debug(f'creating src.Tg.tgapi.download_doclist coroutine and adding to the event loop')
        await tgapi.download_doclist(
            [d.get_loc() for d in self.stickers],
            [tgapi.DocName(d.filename, d.doc_mimetype) for d in self.stickers],
            gvars.CACHEPATH + self.sn + os.sep,
            True
        )

    async def download_thumb(self):
        """
        Downloads the thumbnail of this stickerpack to the cache folder
        :return:
        """
        if self.thumb is None:
            warning("This pack doesn't have a dedicated thumb! Use the first sticker in the pack as the thumbnail\n")
            return
        else:
            info(f'Downloading pack thumbnail for pack {self.sn} and saving to cache')
            debug(f'creating src.Tg.tgapi.download_file coroutine and adding to the event loop')
            await gvars.client.download_file(
                InputStickerSetThumb(InputStickerSetShortName(self.sn), self.thumb.version),
                gvars.CACHEPATH + self.sn + os.sep + 'thumb.' + ('tgs' if self.is_animated else 'webp')
            )

    def get_thumb_path(self) -> str | None:
        """
        Gets the local file location of the thumbnail of the pack. If no such file exists, the method returns None
        :return: The relative string path of the thumbnail of the pack. Returns None if the file doesn't exist.
        """
        fpath: str = (gvars.CACHEPATH + self.sn + os.sep) + \
                     ('thumb' if self.thumb is not None else str(self.stickers[0].doc_id)) + \
                     ('.tgs' if self.is_animated else '.webp')
        if not os.path.exists(fpath): return None
        return fpath

    async def update_meta(self):
        """
        Redownloads the metadata associated with this sticker pack
        :return:
        """
        info(f'Updating metadata for pack {self.sn}')
        npack: TgStickerPack = generate(await tgapi.get_stickerset(self.sn))
        self.id = npack.id
        self.access_hash = npack.access_hash
        self.name = npack.access_hash
        self.sn = npack.sn
        self.size = npack.size
        self.hash = npack.hash
        self.is_animated = npack.is_animated
        self.thumb = npack.thumb
        self.stickers = npack.thumb
        debug('creating download_thumb coroutine and adding to the event loop')
        await self.download_thumb()
        debug('serializing pack metadata to cache')
        serialize_pack(self)

    async def update_all(self):
        """
        Upadtes all information associated with this sticker pack, including redownloading all stickers
        :return:
        """
        info(f'Updating all cached information for pack {self.sn}')
        await self.update_meta()
        await self.download_stickers()


def generate(sset: ParentSet) -> TgStickerPack:
    """
    Generates a TgStickerPack object from the StickerSet object from telegram
    :param sset: The StickerSet object from telegram
    :return: The TgStickerPack object assocated with the input StickerSet object
    """
    info(f"Generating TgStickerPack object for StickerSet {sset.set.short_name}")
    e: dict[int, str] = {}
    p: StickerPack
    for p in sset.packs:
        for d in p.documents:
            e[d] = ''.join(sorted((e.get(d, '') + p.emoticon)))
    tgs: list[TgSticker] = []
    for d in sset.documents:
        tgs.append(TgSticker(d, e.get(d.id, ''), sset.set.short_name))

    return TgStickerPack(sset.set, tgs, generate_thumb(sset))


def generate_thumb(sset: Union[ParentSet, StickerSet]) -> Union[TgPackThumb, None]:
    """
    Generates the TgPackThumb object from the telegram StickerSet object
    :param sset: The telegram StickerSet object
    :return: a TgPackThumb associated with the input StickerSet
    """
    if isinstance(sset, ParentSet): sset = sset.set
    info(f"Generating TgPackThumb object for {sset.short_name}")
    if sset.thumbs is None or len(sset.thumbs) == 0 or sset.thumb_version is None: return None
    ps: PhotoSize = sset.thumbs[0]
    if type(ps) != PhotoSize: return None # TODO thumbs can include PhotoPathObject, account for this!!
    return TgPackThumb(sset.short_name, ps.h, ps.w, ps.size, sset.thumb_dc_id, sset.thumb_version)


async def get_pack(sn: str, force_get_new: bool = False, force_redownload_stickers: bool = False) -> TgStickerPack:
    """
    Gets a TgStickerPack of a specified short name. If the pack is already cached on the user's local machine, then
    the program will retrieve from the cache. If it is not saved, or the method is flagged to download a new copy, then
    The program will call Telegram's servers and generate a new copy and cache it.
    :param sn: The shortname of the desired stickerpack
    :param force_get_new: If True, forces the system to redownload the StickerSet object from Telegram
    :param force_redownload_stickers: If True, forces the system to redownload all sticker pack images to cache
    :return:
    """
    info(f'Generating local data for pack {sn}')
    if force_redownload_stickers and not force_get_new:
        debug('creating new TgStickerPack object. download_stickers coroutine created and added to the event loop')
        tgpack: TgStickerPack = deserialize_pack(sn)
        await tgpack.download_stickers()
        return tgpack
    if check_pack_saved(sn) and not force_get_new:
        debug(f'deserializing pack {sn} from local cache')
        return deserialize_pack(sn)
    info(f'Sticker set {sn} not saved in local cache, downloading from Telegram')
    debug('creating src.Tg.tgapi.get_stickerset coroutine and adding to the event loop')
    sset: StickerSet = await tgapi.get_stickerset(sn)
    tgpack: TgStickerPack = generate(sset)
    debug(f'Serializing {sn} to local cache')
    serialize_pack(tgpack)
    debug('creating tgpack.download_stickers coroutine and adding to the event loop')
    await tgpack.download_stickers()
    if tgpack.thumb is not None: await tgpack.download_thumb()
    return tgpack


def serialize_pack(pack: TgStickerPack):
    """
    Serializes a sticker pack
    :param pack: The pack to serialize
    :return: None
    """
    info(f'Serializing Metadata for for {pack.sn} to local cache')
    utils.serialize(pack, gvars.CACHEPATH + pack.sn + os.sep, pack.sn + '.json')


def check_pack_saved(sn: str) -> bool:
    """
    Checks if a pack is saved on the local system
    :param sn: The shortname of the desired pack
    :return: Whether the pack is saved or not
    """
    info(f'Checking if pack {sn} is saved on the local cache')
    return utils.check_file(gvars.CACHEPATH + sn + os.sep + sn + '.json')


def deserialize_pack(sn: str) -> TgStickerPack:
    """
    Deserializes the desired sticker pack
    :param sn: The shortname of the desired pack
    :return: The TgStickerPack object
    """
    info(f'Deserializing pack {sn} from local cache')
    return utils.deserialize(gvars.CACHEPATH + sn + os.sep + sn + '.json')


async def get_owned_packs() -> list[str]:
    """
    Gets all the sticker packs that the user owns
    :return: A list of strs containing the shortnames of all the user's owned packs
    """
    try:
        lst = utils.deserialize(gvars.get_current_user_path() + gvars.PACKS_FNAME)
        useless_var = lst[0] + ''
        return lst
    except:
        pass
    return await update_owned_packs()


async def update_owned_packs() -> list[str]:
    """
    Gets all the sticker packs that the user owns but bypasses the caches and saves a new copy
    :return: A list of strs containing the shortnames of all the users's owned packs
    """
    lst = await tgapi.get_owned_stickerset_shortnames()
    utils.serialize(lst, gvars.get_current_user_path(), gvars.PACKS_FNAME)
    return lst

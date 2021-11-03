import os
from typing import Union

from telethon.tl.types import Document, DocumentAttributeImageSize, StickerSet, StickerPack, \
    DocumentAttributeFilename, InputDocumentFileLocation, InputStickerSetThumb, InputStickerSetShortName, PhotoSize
from telethon.tl.types.messages import StickerSet as ParentSet

from src import gvars, utils
import tgapi
import jsonpickle


class TgSticker:
    # TODO Docstring
    def __init__(self, doc: Document, emojis: str, parent_sn: str):
        # TODO Docstring
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
        # TODO Docstring
        return InputDocumentFileLocation(
            self.doc_id,
            self.doc_access_hash,
            self.doc_fileref,
            '0'
        )


class TgPackThumb:
    # TODO Docstring
    def __init__(self, parent_shortname: str, height: int, width: int, size: int, dc_id: int, version: int):
        # TODO Docstring
        self.parent_sn: str = parent_shortname
        self.height: int = height
        self.width: int = width
        self.size: int = size
        self.dc_id: int = dc_id
        self.version: int = version

    def get_loc(self):
        # TODO Docstring
        return InputStickerSetThumb(InputStickerSetShortName(self.parent_sn), self.version)


class TgStickerPack:
    # TODO Docstring
    def __init__(self, sset: StickerSet, stickers: list[TgSticker], thumb: Union[TgPackThumb, None]):
        # TODO Docstring
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
        # TODO Docstring
        await tgapi.download_doclist(
            [d.get_loc() for d in self.stickers],
            [tgapi.DocName(d.filename, d.doc_mimetype) for d in self.stickers],
            gvars.CACHEPATH + self.sn + os.sep,
            True
        )

    async def download_thumb(self):
        # TODO Docstring
        if self.thumb is None:
            print("This pack doesn't have a dedicated thumb! Use the first sticker in the pack as the thumbnail\n")
            return
        else:
            await gvars.client.download_file(
                InputStickerSetThumb(InputStickerSetShortName(self.sn), self.thumb.version),
                gvars.CACHEPATH + self.sn + os.sep + 'thumb.' + ('tgs' if self.is_animated else 'webp')
            )

    async def update_meta(self):
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
        await self.download_thumb()
        serialize_pack(self)

    async def update_all(self):
        await self.update_meta()
        await self.download_stickers()


def generate(sset: ParentSet) -> TgStickerPack:
    # TODO Docstring
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
    # TODO Docstring
    if isinstance(sset, ParentSet): sset = sset.set
    if sset.thumbs is None or len(sset.thumbs) == 0 or sset.thumb_version is None: return None
    ps: PhotoSize = sset.thumbs[0]
    return TgPackThumb(sset.short_name, ps.h, ps.w, ps.size, sset.thumb_dc_id, sset.thumb_version)


async def get_pack(sn: str, force_get_new: bool = False, force_download_stickers: bool = False) -> TgStickerPack:
    # TODO Docstring
    if force_download_stickers and not force_get_new:
        tgpack: TgStickerPack = cache.deserialize_pack(sn)
        await tgpack.download_stickers()
        return tgpack
    if check_pack_saved(sn) and not force_get_new:
        return deserialize_pack(sn)
    sset: StickerSet = await tgapi.get_stickerset(sn)
    tgpack: TgStickerPack = generate(sset)
    serialize_pack(tgpack)
    await tgpack.download_stickers()
    return tgpack

def serialize_pack(pack: TgStickerPack):
    # TODO Docstring
    jsonpickle.set_encoder_options('json', indent=4)
    ser: str = jsonpickle.encode(pack, unpicklable=True, keys=True)
    utils.write_txt(ser, gvars.CACHEPATH + pack.sn + os.sep, pack.sn, 'json')


def check_pack_saved(sn: str) -> bool:
    # TODO Docstring
    return utils.check_file(gvars.CACHEPATH + sn + os.sep + sn + '.json')


def deserialize_pack(sn: str) -> TgStickerPack:
    # TODO Docstring
    ser: str = utils.read_txt(gvars.CACHEPATH + sn + os.sep + sn + '.json')
    return jsonpickle.decode(ser, keys=True, classes=TgStickerPack)

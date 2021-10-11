import os

import jsonpickle

import gvars
import utils
import stickers


def serialize_pack(pack: stickers.TgStickerPack):
    # TODO Docstring
    jsonpickle.set_encoder_options('json', indent=4)
    ser: str = jsonpickle.encode(pack, unpicklable=True, keys=True)
    utils.write_txt(ser, gvars.CACHEPATH + pack.sn + os.sep, pack.sn, 'json')


def check_pack_saved(sn: str) -> bool:
    # TODO Docstring
    return utils.check_file(gvars.CACHEPATH + sn + os.sep + sn + '.json')


def deserialize_pack(sn: str) -> stickers.TgStickerPack:
    # TODO Docstring
    ser: str = utils.read_txt(gvars.CACHEPATH + sn + os.sep + sn + '.json')
    return jsonpickle.decode(ser, keys=True, classes=stickers.TgStickerPack)

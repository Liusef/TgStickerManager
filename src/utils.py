import os

from telethon.tl.tlobject import TLObject
from telethon.tl.types import Document, DocumentAttributeFilename


def raise_exception_no_err(val=None):
    """
    Raises an exception and prints out the stringified value of val

    :param val: The object that you want to print out the thing from
    :raises: Exception
    """
    var = ""
    objstr: str = val.stringify() if isinstance(val, TLObject) else str(val)
    if (val != None):
        var = '\n' + str(type(val)) + '\n' + str(val)
    raise Exception("Program called sign_in, failed to signin, connect, send auth code, or receive other error\n" + var)


def get_path_ext(path: str, fallback_ext: str = '') -> str:
    """
    Gets the extension of a file from its filename or path

    :param path: The Path to retrieve the extension from
    :param fallback_ext: The extension to use if the program fails to find the extension
    :return: The file extension
    """
    # TODO Consider replacing some of the functionality by using MIME types
    i: int = path.rfind('.', 0, len(path))
    return path[i + 1:] if (i != -1) else fallback_ext


def check_file(file: str) -> bool:
    # TODO Docstring
    return os.path.exists(file)


def check_path(path: str) -> str:
    """
    Checks if a given path exists on the local device. If the path doesn't exist, the program will create it

    :param path: The path to check
    :return: The path that was input
    """
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def check_all_paths(paths: list[str]):
    """
    Checks if all paths in an array exist

    :param paths: The array of paths to check
    :return: None
    """
    for p in paths:
        check_path(p)


def read_txt(file: str) -> str:
    # TODO Docstring
    with open(file, 'r') as f:
        return f.read()


# TODO Does this even work lmfao
def write_txt(txt: str, path: str, fname: str, ext: str, encode: str = 'utf8'):
    """
    Writes text to a file

    :param txt: The text to write to file
    :param path: The path to where the file is
    :param fname: The filename of the file to write to
    :return: None
    """
    ext = ('.' + ext) if (len(ext) > 0) else ext
    f = open(check_path(path) + fname + ext, 'w', encoding=encode)
    f.write(txt)
    f.close()


def get_doc_attr(doc: Document, attr_type: type):
    # TODO add docstring
    lst: list[attr_type] = [o for o in doc.attributes if isinstance(o, attr_type)]
    if (len(lst) == 0): return None
    return lst[0]


def get_attr_filename(f: Document, fallback: str = "") -> str:
    """
    Returns the filename attribute of a Document if present

    :param f: The Document in question
    :param fallback: The fallback string to return if the document doesn't have the filename attribute
    :return: The filename of the document
    """
    attr: DocumentAttributeFilename = get_doc_attr(f, DocumentAttributeFilename)
    if attr is None: return fallback
    return attr.file_name

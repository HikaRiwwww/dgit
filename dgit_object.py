import hashlib
import sys
import zlib

from dgit_repository import repo_file


class DgitObject:
    repo = None

    def __init__(self, repo, data=None):
        self.repo = repo
        if data:
            self.deserialize(data)

    def serialize(self):
        raise NotImplemented

    def deserialize(self, data):
        raise NotImplemented


class DgitCommit(DgitObject):
    pass


class DgitTree(DgitObject):
    pass


class DgitTag(DgitObject):
    pass


class DgitBlob(DgitObject):
    fmt = b'blob'

    def serialize(self):
        return self.blobdata

    def deserialize(self, data):
        self.blobdata = data


def object_find(repo, name, fmt=None, follow=True):
    """
    # todo
    :param repo:
    :param name:
    :param fmt:
    :param follow:
    :return:
    """
    return name


def object_read(repo, sha):
    """
    sample:
    00000000  63 6f 6d 6d 69 74 20 31  30 38 36 00 74 72 65 65  |commit 1086.tree|
    00000010  20 32 39 66 66 31 36 63  39 63 31 34 65 32 36 35  | 29ff16c9c14e265|
    00000020  32 62 32 32 66 38 62 37  38 62 62 30 38 61 35 61  |2b22f8b78bb08a5a|

    :param repo:
    :param sha:
    :return:
    """
    path = repo_file(repo, "objects", sha[:2], sha[2:])
    with open(path, "rb") as f:
        raw = zlib.decompress(f.read())

    # 判断是commit还是tree或者tag之类的类型
    x = raw.find(b' ')
    fmt = raw[:x]
    y = raw.find(b'\x00', x)
    size = int(raw[x:y].decode('ascii'))
    if size != len(raw) - y - 1:
        raise Exception("size info does not match")

    c = {
        b'commit': DgitCommit,
        b'tree': DgitTree,
        b'tag': DgitTag,
        b'blob': DgitBlob,
    }.get(fmt)
    return c(repo, raw[y + 1:])


def cat_file(repo, obj, fmt=None):
    obj = object_read(repo, object_find(repo, obj, fmt=fmt))
    sys.stdout.buffer.write(obj.serialize())


def object_write(obj: DgitObject, actually_write=True):
    data = obj.serialize()
    result = obj.fmt + b' ' + str(len(data)).encode() + b'\x00' + data
    sha = hashlib.sha1(result).hexdigest()

    if actually_write:
        path = repo_file(obj.repo, "objects", sha[:2], sha[2:], mkdir=actually_write)

        with open(path, 'wb') as f:
            f.write(zlib.compress(result))

    return sha

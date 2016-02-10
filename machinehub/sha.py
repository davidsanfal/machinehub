import hashlib
from datetime import datetime
import zipfile


def dict_sha1(value=None):
    value = value or {}
    md = hashlib.sha1()
    a_sorted_list = [(key, value[key]) for key in sorted(value.keys())]
    md.update(str(a_sorted_list).encode('utf-8'))
    return md.hexdigest()


def date_sha1():
    md = hashlib.sha1()
    md.update(str(datetime.now()).encode('utf-8'))
    return md.hexdigest()


def zip_sha1(file_path):
    # http://stackoverflow.com/questions/1869885/calculating-sha1-of-a-file
    md = hashlib.sha1()
    with zipfile.ZipFile(file_path, "r") as z:
        files = z.namelist()
        for f in files:
            content = z.read(f)
            md.update(("blob " + str(len(content)) + "\0" + str(content)).encode('utf-8'))
    return md.hexdigest()

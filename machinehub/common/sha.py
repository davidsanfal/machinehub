import hashlib
from datetime import datetime


def dict_sha1(value=None):
    if not value:
        return date_sha1()
    else:
        md = hashlib.sha1()
        a_sorted_list = [(key, value[key]) for key in sorted(value.keys())]
        md.update(str(a_sorted_list))
        return md.hexdigest()


def date_sha1():
    md = hashlib.sha1()
    md.update(str(datetime.now()))
    return md.hexdigest()

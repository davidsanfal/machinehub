import hashlib
from datetime import datetime


def dict_sha1(value):
    md = hashlib.sha1()
    if not value:
        md.update(str(datetime.now()))
    else:
        a_sorted_list = [(key, value[key]) for key in sorted(value.keys())]
        md.update(str(a_sorted_list))
    return md.hexdigest()

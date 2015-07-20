import hashlib


def dict_sha1(value):
    md = hashlib.sha1()
    a_sorted_list = [(key, value[key]) for key in sorted(value.keys())]
    md.update(str(a_sorted_list))
    return md.hexdigest()

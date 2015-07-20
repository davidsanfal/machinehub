import fnmatch
from werkzeug.utils import secure_filename
import os
from machinehub.errors import MachinehubException


def allowed_file(filename, allowed_extension):
    if '*' in allowed_extension:
        return True
    try:
        ext = filename.rsplit('.', 1)[1]
        return ext in allowed_extension
    except:
        return None in allowed_extension


def pattern_allowed_file(filename, patterns):
    for pattern in patterns:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False


def save(resource, dest, extensions=None, pattern_extensions=None):
    if not resource:
        return None
    elif not (extensions and pattern_extensions) and (extensions or pattern_extensions):
        allowed = False
        if extensions:
            allowed = allowed_file(resource.filename, extensions)
        elif pattern_extensions:
            allowed = pattern_allowed_file(resource.filename, pattern_extensions)
        if allowed:
            filename = secure_filename(resource.filename)
            file_path = os.path.join(dest, filename)
            resource.save(file_path)
            return file_path
        return None
    else:
        raise MachinehubException('Define only one parameter "extensions" or "pattern_extensions"')

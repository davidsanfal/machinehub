import fnmatch
from werkzeug.utils import secure_filename
import os
from machinehub.common.errors import MachinehubException, NotMachineHub, ForbiddenException
from machinehub.config import MACHINES_FOLDER, MACHINEFILE
import zipfile
import shutil
from machinehub.server.app.services.permission_service import user_can_edit


ALLOWED_EXTENSIONS = ['zip']


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
    if (extensions and pattern_extensions) and (extensions or pattern_extensions):
        raise MachinehubException('Define only one parameter "extensions" or "pattern_extensions"')
    allowed = False
    if extensions:
        allowed = allowed_file(resource.filename, extensions)
    elif pattern_extensions:
        allowed = pattern_allowed_file(resource.filename, pattern_extensions)
    if allowed:
        filename = secure_filename(resource.filename)
        name, _ = os.path.splitext(filename)
        try:
            os.mkdir(os.path.join(dest, name))
        except:
            pass
        file_path = os.path.join(dest, name, filename)
        resource.save(file_path)
        return file_path
    else:
        return None


def extract_zip(file_path):
    try:
        name, ext = os.path.splitext(os.path.basename(file_path))
        if user_can_edit(name):
            with zipfile.ZipFile(file_path, "r") as z:
                files_in_zip = z.namelist()
                if not len(files_in_zip) == 1:
                    _name, ext = os.path.splitext(files_in_zip[0])
                    if ext == '' and _name == '%s/' % name and \
                       all(s.startswith('%s/' % name) for s in files_in_zip):
                        z.extractall(MACHINES_FOLDER)
                    elif '%s.py' % name in files_in_zip and MACHINEFILE in files_in_zip:
                        z.extractall(os.path.join(MACHINES_FOLDER, name))
                else:
                    os.remove(file_path)
            return name
        else:
            raise ForbiddenException('You can\'t create the machine: %s' % name)
    except NotMachineHub:
        shutil.rmtree(os.path.join(MACHINES_FOLDER, os.path.basename(file_path)))


def upload_machine(uploaded_file, machines_model):
    file_path = save(uploaded_file, MACHINES_FOLDER, ALLOWED_EXTENSIONS)
    if file_path:
        name = extract_zip(file_path)
        machine_path = os.path.join(MACHINES_FOLDER, name, '%s.py' % name)
        machinefile_path = os.path.join(MACHINES_FOLDER, name, MACHINEFILE)
        if os.path.exists(machine_path) and os.path.exists(machinefile_path):
            return machines_model.update(machinefile_path, name)
        else:
            return None

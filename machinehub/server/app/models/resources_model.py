import fnmatch
from werkzeug.utils import secure_filename
import os
from machinehub.common.errors import MachinehubException, NotMachineHub
from machinehub.config import MACHINES_FOLDER, MACHINEFILE
import zipfile
import shutil


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


def save(resources, dest, extensions=None, pattern_extensions=None):
    file_paths = []
    if not resources:
        return None
    elif not (extensions and pattern_extensions) and (extensions or pattern_extensions):
        for resource in resources:
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
                file_paths.append(file_path)
        return file_paths if not file_paths == [] else None
    else:
        raise MachinehubException('Define only one parameter "extensions" or "pattern_extensions"')


def extract_zip(file_path):
    try:
        name, ext = os.path.splitext(os.path.basename(file_path))
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
    except NotMachineHub:
        shutil.rmtree(os.path.join(MACHINES_FOLDER, os.path.basename(file_path)))


def upload_machines(uploaded_files, machines_model):
    names = []
    file_paths = save(uploaded_files, MACHINES_FOLDER, ALLOWED_EXTENSIONS)
    if file_paths:
        for file_path in file_paths:
            name = extract_zip(file_path)
            machine_path = os.path.join(MACHINES_FOLDER, name, '%s.py' % name)
            machinefile_path = os.path.join(MACHINES_FOLDER, name, MACHINEFILE)
            if os.path.exists(machine_path) and os.path.exists(machinefile_path):
                names.append(machines_model.update(machinefile_path, name))
    return names

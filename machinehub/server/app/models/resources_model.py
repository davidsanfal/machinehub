import fnmatch
from werkzeug.utils import secure_filename
import os
from machinehub.common.errors import MachinehubException, NotMachineHub
from machinehub.config import MACHINES_FOLDER
from machinehub.server.app.controllers.machine_controller import ALLOWED_EXTENSIONS
import zipfile
import shutil
import sys


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


def upload_files(uploaded_files, machines_model):
    file_paths = save(uploaded_files, MACHINES_FOLDER, ALLOWED_EXTENSIONS)
    if file_paths:
        names = []
        for file_path in file_paths:
            try:
                name, ext = os.path.splitext(os.path.basename(file_path))
                if ext == '.zip':
                    machine_path = os.path.join(MACHINES_FOLDER, name, '%s.py' % name)
                    with zipfile.ZipFile(file_path, "r") as z:
                        files_in_zip = z.namelist()
                        print files_in_zip
                        if not len(files_in_zip) == 1:
                            _name, ext = os.path.splitext(files_in_zip[0])
                            if ext == '' and _name == '%s/' % name and \
                               all(s.startswith('%s/' % name) for s in files_in_zip):
                                z.extractall(MACHINES_FOLDER)
                            elif '%s.py' % name in files_in_zip:
                                z.extractall(os.path.join(MACHINES_FOLDER, name))
                        else:
                            os.remove(file_path)
                            machine_path = None
                    if machine_path:
                        sys.path.append(os.path.join(MACHINES_FOLDER, name))
                        names.append(machines_model.update(machine_path))
                else:
                    names.append(machines_model.update(file_path))
            except NotMachineHub:
                shutil.rmtree(os.path.join(MACHINES_FOLDER, os.path.basename(file_path)))
                pass
        return names
    return None

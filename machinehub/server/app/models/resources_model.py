import fnmatch
from werkzeug.utils import secure_filename
import os
from machinehub.common.errors import MachinehubException, NotMachineHub, ForbiddenException,\
    InvalidNameException
from machinehub.config import MACHINES_FOLDER, MACHINEFILE
import zipfile
import shutil
from machinehub.server.app.services.permission_service import user_can_edit
from flask_login import current_user
from machinehub.common.model.machine_name import MachineName


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
            machine_name = "{user}/{machine}".format(user=current_user.username,
                                                     machine=name)
            name = MachineName(machine_name)
        except InvalidNameException as e:
            raise ForbiddenException(e)
        try:
            os.makedirs(os.path.join(dest, name))
        except:
            pass
        file_path = os.path.join(dest, name, filename)
        resource.save(file_path)
        return file_path
    else:
        return None


def extract_zip(file_path):
    machine_name = None
    try:
        name, ext = os.path.splitext(os.path.basename(file_path))
        machine_name = "{user}/{machine}".format(user=current_user.username,
                                                 machine=name)
        machine_name = MachineName(machine_name)
        if user_can_edit(machine_name):
            with zipfile.ZipFile(file_path, "r") as z:
                files_in_zip = z.namelist()
                if not len(files_in_zip) == 1:
                    _name, ext = os.path.splitext(files_in_zip[0])
                    if ext == '' and _name == '%s/' % name and \
                       all(s.startswith('%s/' % name) for s in files_in_zip):
                        z.extractall(os.path.join(MACHINES_FOLDER, current_user.username))
                    elif '%s.py' % name in files_in_zip and MACHINEFILE in files_in_zip:
                        z.extractall(os.path.join(MACHINES_FOLDER, machine_name))
                else:
                    os.remove(file_path)
            return machine_name
        else:
            raise ForbiddenException('You can\'t create the machine: %s' % machine_name.name)
    except NotMachineHub:
        shutil.rmtree(os.path.join(MACHINES_FOLDER, os.path.basename(file_path)))
    except InvalidNameException as e:
        if machine_name and os.path.exists(os.path.join(MACHINES_FOLDER, machine_name)):
            shutil.rmtree(os.path.join(MACHINES_FOLDER, machine_name))
        raise ForbiddenException(e)


def upload_machine(uploaded_file, machines_model):
    file_path = save(uploaded_file, MACHINES_FOLDER, ALLOWED_EXTENSIONS)
    if file_path:
        machine_name = extract_zip(file_path)
        machine_path = os.path.join(MACHINES_FOLDER, machine_name, '%s.py' % machine_name.name)
        machinefile_path = os.path.join(MACHINES_FOLDER, machine_name, MACHINEFILE)
        if os.path.exists(machine_path) and os.path.exists(machinefile_path):
            return machines_model.update(machinefile_path, machine_name)
        else:
            return None

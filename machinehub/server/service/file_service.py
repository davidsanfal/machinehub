from machinehub.model.machine_name import MachineName
from machinehub.errors import InvalidNameException, ForbiddenException,\
    NotMachineHub
import os
import zipfile
from machinehub.config import MACHINES_FOLDER, MACHINEFILE
import shutil


ALLOWED_EXTENSIONS = ['zip']


class FileService():

    def __init__(self, authorizer):
        self.authorizer = authorizer

    def allowed_file(self, filename, allowed_extension):
        if '*' in allowed_extension:
            return True
        try:
            ext = filename.rsplit('.', 1)[1]
            return ext in allowed_extension
        except:
            return None in allowed_extension

    def save(self, resource, dest, extensions, user_auth):
        if not resource:
            return None
        filename = resource.filename
        if self.allowed_file(filename, extensions):
            name, _ = os.path.splitext(filename)
            try:
                machine_name = "{user}/{machine}".format(user=user_auth, machine=name)
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

    def extract_zip(self, file_path, user_auth):
        machine_name = None
        try:
            name, ext = os.path.splitext(os.path.basename(file_path))
            machine_name = "{user}/{machine}".format(user=user_auth, machine=name)
            machine_name = MachineName(machine_name)
            if self.authorizer.user_can_edit(machine_name):
                with zipfile.ZipFile(file_path, "r") as z:
                    files_in_zip = z.namelist()
                    if not len(files_in_zip) == 1:
                        _name, ext = os.path.splitext(files_in_zip[0])
                        if ext == '' and _name == '%s/' % name and \
                           all(s.startswith('%s/' % name) for s in files_in_zip):
                            z.extractall(os.path.join(MACHINES_FOLDER, user_auth))
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

    def upload_machine(self, uploaded_file, machines_model, auth_user):
        file_path = self.save(uploaded_file, MACHINES_FOLDER, ALLOWED_EXTENSIONS)
        if file_path:
            machine_name = self.extract_zip(file_path, auth_user)
            return machine_name

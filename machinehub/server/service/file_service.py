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

    def save(self, resource, dest, extensions, auth_user):
        if not resource:
            return None
        filename = resource.filename
        if self.allowed_file(filename, extensions):
            name, _ = os.path.splitext(filename)
            try:
                machine_name = "{user}/{machine}".format(user=auth_user, machine=name)
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

    def extract_zip(self, file_path, auth_user):
        machine_name = None
        try:
            name, ext = os.path.splitext(os.path.basename(file_path))
            machine_name = "{user}/{machine}".format(user=auth_user, machine=name)
            machine_name = MachineName(machine_name)
            with zipfile.ZipFile(file_path, "r") as z:
                files_in_zip = z.namelist()
                if not len(files_in_zip) == 1:
                    _name, ext = os.path.splitext(files_in_zip[0])
                    if ext == '' and _name == '%s/' % name and \
                       all(s.startswith('%s/' % name) for s in files_in_zip):
                        print(os.path.join(MACHINES_FOLDER, auth_user))
                        z.extractall(os.path.join(MACHINES_FOLDER, auth_user))
                    elif '%s.py' % name in files_in_zip and MACHINEFILE in files_in_zip:
                        z.extractall(os.path.join(MACHINES_FOLDER, machine_name))
                    os.remove(file_path)
                else:
                    raise NotMachineHub()
            return machine_name
        except NotMachineHub:
            shutil.rmtree(os.path.join(MACHINES_FOLDER, os.path.basename(file_path)))
        except InvalidNameException as e:
            if machine_name and os.path.exists(os.path.join(MACHINES_FOLDER, machine_name)):
                shutil.rmtree(os.path.join(MACHINES_FOLDER, machine_name))
            raise ForbiddenException(e)

    def upload_machine(self, uploaded_file, dest, auth_user):
        file_path = self.save(uploaded_file, dest, ALLOWED_EXTENSIONS, auth_user)
        machine_name = self.extract_zip(file_path, auth_user)
        return machine_name

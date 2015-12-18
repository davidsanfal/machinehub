import os
import shutil
from machinehub.config import MACHINES_FOLDER, MACHINESOUT, MACHINEFILE
from machinehub.server.service.file_service import FileService
from machinehub.machinefile_loader import load_machinefile
from machinehub.docker.dockerizer import create_image, dockerize
from machinehub.errors import NotMachineHub
from machinehub.sha import date_sha1
import json


class MachineManager():

    def __init__(self, autorizer):
        self.file_service = FileService(autorizer)

    def __contains__(self, name):
        if os.path.exists(os.path.join(MACHINES_FOLDER, name)):
            return True
        else:
            return False

    def new(self, resource, auth_user):
        machine_name = self.file_service.upload_machine(resource, auth_user)
        create_image(machine_name, [], [])

    def read(self, name):
        try:
            machinefile_path = os.path.join(MACHINES_FOLDER, name, MACHINEFILE)
            machinefile = load_machinefile(machinefile_path)
            readme_path = os.path.join(MACHINES_FOLDER, name, 'readme.md')
            readme = None
            if os.path.exists(readme_path):
                with open(readme_path, 'r') as f:
                    readme = f.read()

            return machinefile, readme
        except NotMachineHub:
            raise NotMachineHub()
        return name

    def machine(self, name):
        if os.path.exists(os.path.join(MACHINES_FOLDER, name)):
                pass

    def delete(self, name):
        if os.path.exists(os.path.join(MACHINES_FOLDER, name)):
            shutil.rmtree(os.path.join(MACHINES_FOLDER, name))

    def work(self, values, name):
        machine_id = date_sha1()
        with open(os.path.join(MACHINES_FOLDER, name, 'input%s.json' % machine_id), 'w+') as f:
            f.write(json.dumps(values))
        dockerize(name, machine_id)
        os.remove(os.path.join(MACHINES_FOLDER, name, 'input%s.json' % machine_id))

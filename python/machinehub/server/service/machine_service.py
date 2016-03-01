import os
import shutil
from machinehub.config import MACHINES_FOLDER, MACHINESOUT, MACHINEFILE,\
    UPLOAD_FOLDER
from machinehub.server.service.file_service import FileService
from machinehub.machinefile_loader import load_machinefile
from machinehub.docker.dockerizer import create_image, dockerize
from machinehub.errors import NotMachineHub, NotFoundException,\
    RequestErrorException
from machinehub.sha import dict_sha1
import json


types = {'int': int,
         'float': float}


class MachineManager():

    def __init__(self, autorizer):
        self.file_service = FileService(autorizer)

    def __contains__(self, machine_name):
        if os.path.exists(os.path.join(MACHINES_FOLDER, machine_name)):
            return True
        else:
            raise False

    def machine_exist(self, machine_name):
        if machine_name not in self:
            raise NotFoundException()

    def extract_zip(self, uploaded_file, machine_name):
        dest = os.path.join(MACHINES_FOLDER, machine_name)
        machine_id = self.file_service.extract_zip_request(uploaded_file, dest)
        json_path = os.path.join(MACHINES_FOLDER,
                                 machine_name,
                                 'input%s' % machine_id,
                                 'input.json')
        json_info = {}
        if os.path.exists(json_path):
            with open(json_path, "r") as j:
                json_info = json.loads(j.read())
        return machine_id, json_info

    def new(self, uploaded_file, auth_user):
        machine_name = self.file_service.upload_machine(uploaded_file,
                                                        MACHINES_FOLDER,
                                                        auth_user)
        create_image(machine_name, [], [], 'freecad')
        return True

    def read(self, machine_name):
        self.machine_exist(machine_name)
        try:
            machinefile_path = os.path.join(MACHINES_FOLDER, machine_name, MACHINEFILE)
            machinefile = load_machinefile(machinefile_path)
            readme_path = os.path.join(MACHINES_FOLDER, machine_name, 'readme.md')
            readme = None
            if os.path.exists(readme_path):
                with open(readme_path, 'r') as f:
                    readme = f.read()

            return machinefile, readme
        except NotMachineHub:
            raise NotMachineHub()

    def delete(self, machine_name):
        self.machine_exist(machine_name)
        if os.path.exists(os.path.join(MACHINES_FOLDER, machine_name)):
            shutil.rmtree(os.path.join(MACHINES_FOLDER, machine_name))

    def work(self, machine_name, data, machine_id=None):
        self.machine_exist(machine_name)
        machinefile, _ = self.read(machine_name)
        if type(data) is not dict:
            return "WOLOLO"
        values = {}
        for name, _type, _, _, _ in machinefile.inputs:
            value = data.get(name, None)
            if not value:
                raise RequestErrorException()
            if types.get(_type, None):
                values[name] = types[_type](value)
            else:
                values[name] = value
        current_folder = os.getcwd()
        os.chdir(os.path.join(MACHINES_FOLDER, machine_name))
        machine_id = machine_id or dict_sha1(data)
        file_name = '%s_%s.stl' % (machine_name.replace('/', '_'), machine_id)
        file_url = os.path.join('machines', machine_name, MACHINESOUT, file_name)
        file_path = os.path.join(UPLOAD_FOLDER, file_url)
        input_folder = os.path.join(MACHINES_FOLDER, machine_name, 'input%s' % machine_id)
        if not os.path.exists(file_path) or not values:
            values['file_path'] = file_name
            json_info = os.path.join(MACHINES_FOLDER, machine_name, 'input%s.json' % machine_id)
            with open(json_info, 'w+') as f:
                f.write(json.dumps(values))
            dockerize(machine_name, machine_id)
            os.remove(json_info)
        if os.path.exists(input_folder):
            shutil.rmtree(input_folder)

        os.chdir(current_folder)
        return os.path.join(machine_name, file_name)

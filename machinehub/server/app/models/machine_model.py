import os
from machinehub.config import MACHINES_FOLDER, MACHINESOUT, MACHINEFILE
from machinehub.common.errors import NotFoundException, NotMachineHub
import shutil
from machinehub.common.machinefile_loader import load_machinefile
import json
from machinehub.common.sha import date_sha1
from machinehub.docker.dockerizer import dockerize, create_image


class MachineModel(object):
    _instance = None

    def __init__(self):
        self._machines = {}
        self.search()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MachineModel, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __contains__(self, machine):
        if machine in self._machines.keys():
            return True
        else:
            return False

    def search(self):
        machine_folders = [p for p in os.listdir(MACHINES_FOLDER)
                           if os.path.isdir(os.path.join(MACHINES_FOLDER, p))]

        for name in machine_folders:
            try:
                machinefile = os.path.join(MACHINES_FOLDER, name, MACHINEFILE)
                if os.path.exists(machinefile):
                    doc, inputs = load_machinefile(machinefile)
                    self._machines[name] = {'doc': doc,
                                            'inputs': inputs}
                    create_image(name, [], [])
            except NotMachineHub:
                continue

    @property
    def all_machines(self):
        info = []
        for machine in self._machines.keys():
            info.append((machine, self._machines[machine]['doc']))
        return info

    @property
    def count(self):
        return len(self._machines.keys())

    def update(self, machinefile_path, name):
        try:
            self._add(name, machinefile_path)
        except NotMachineHub:
            raise NotMachineHub()
        return name

    def machine(self, name):
        try:
            machine = self._machines[name]
            return machine['doc'], machine['inputs']
        except:
            raise NotFoundException()

    def delete(self, name):
        if os.path.exists(os.path.join(MACHINES_FOLDER, name)):
            shutil.rmtree(os.path.join(MACHINES_FOLDER, name))
        del self._machines[name]

    def _add(self, name, machinefile_path):
        out_folder = os.path.join(MACHINES_FOLDER, name, MACHINESOUT)
        doc, inputs = load_machinefile(machinefile_path)
        if os.path.exists(out_folder) and name in self._machines.keys():
            shutil.rmtree(out_folder)
        self._machines[name] = {'doc': doc,
                                'inputs': inputs}
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
        create_image(name, [], [])

    def get_machines_for_page(self, page, per_page, count):
        origin = per_page * (page - 1)
        end = origin + per_page
        machines = self._machines.keys()[origin:end] if count > origin + per_page \
            else self._machines.keys()[origin:]
        info = []
        for machine in machines:
            info.append((machine, self._machines[machine]['doc']))
        return info

    def get_last_machines(self):
        info = []
        origin = 0
        if self.count > 7:
            origin = self.count-8
        for machine in self._machines.keys()[origin:]:
            info.append((machine, self._machines[machine]['doc']))
        return info

    def work(self, values, name):
        machine_id = date_sha1()
        with open(os.path.join(MACHINES_FOLDER, name, 'input%s.json' % machine_id), 'w+') as f:
            f.write(json.dumps(values))
        dockerize(name, machine_id)
        os.remove(os.path.join(MACHINES_FOLDER, name, 'input%s.json' % machine_id))

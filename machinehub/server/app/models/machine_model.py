import os
from machinehub.config import MACHINES_FOLDER, MACHINESOUT
from machinehub.common.machine_loader import load_machine
from machinehub.common.errors import NotFoundException, NotMachineHub
import shutil
import sys


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
                sys.path.append(os.path.join(MACHINES_FOLDER, name))
                machine = os.path.join(MACHINES_FOLDER, name, '%s.py' % name)
                if os.path.exists(machine):
                    fn, doc, inputs = load_machine(machine)
                    self._machines[name] = {'fn': fn,
                                            'doc': doc,
                                            'inputs': inputs}
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

    def update(self, file_path):
        try:
            name = os.path.basename(file_path).replace('.py', '')
            self._add(name, file_path)
        except NotMachineHub:
            raise NotMachineHub()
        return name

    def machine(self, name):
        try:
            machine = self._machines[name]
            return machine['fn'], machine['doc'], machine['inputs']
        except:
            raise NotFoundException()

    def delete(self, name):
        if os.path.exists(os.path.join(MACHINES_FOLDER, name)):
            shutil.rmtree(os.path.join(MACHINES_FOLDER, name))
        del self._machines[name]

    def _add(self, name, machine_path):
        objects_folder = os.path.join(MACHINES_FOLDER, name, MACHINESOUT)
        fn, doc, inputs = load_machine(machine_path)
        if name in self._machines.keys():
            shutil.rmtree(objects_folder)
        print name
        self._machines[name] = {'fn': fn,
                                'doc': doc,
                                'inputs': inputs}
        if not os.path.exists(objects_folder):
            os.makedirs(objects_folder)
            shutil.copy2(machine_path, objects_folder)

    def get_machines_for_page(self, page, per_page, count):
        origin = per_page * (page - 1)
        end = origin+per_page
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

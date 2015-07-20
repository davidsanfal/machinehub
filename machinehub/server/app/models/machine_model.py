import glob
import os
from machinehub.config import MACHINES_FOLDER
from machinehub.machine_loader import load_machine
from machinehub.errors import NotFoundException, NotMachineHub
import shutil


class MachineModel(object):
    _instance = None

    def __init__(self):
        self._machines = {}
        self.search

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MachineModel, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @property
    def search(self):
        for machine in glob.glob(os.path.join(MACHINES_FOLDER, '*.py')):
            try:
                fn, doc, inputs = load_machine(machine)
                name = os.path.basename(machine).replace('.py', '')
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
            if name in self._machines.keys():
                shutil.rmtree(os.path.join(MACHINES_FOLDER, name))
            self._add(name)
        except NotMachineHub:
            os.remove(file_path)
            raise NotMachineHub()
        return name

    def machine(self, name):
        try:
            machine = self._machines[name]
            return machine['fn'], machine['doc'], machine['inputs']
        except:
            raise NotFoundException()

    def _add(self, name):
        machine_path = os.path.join(MACHINES_FOLDER, '%s.py' % name)
        objects_folder = os.path.join(MACHINES_FOLDER, name)
        fn, doc, inputs = load_machine(machine_path)
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

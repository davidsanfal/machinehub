import os
from machinehub.config import MACHINES_FOLDER, MACHINESOUT, MACHINEFILE
from machinehub.common.errors import NotFoundException, NotMachineHub
import shutil
from machinehub.common.machinefile_loader import load_machinefile
import json
from machinehub.common.sha import date_sha1
from machinehub.docker.dockerizer import dockerize, create_image
from machinehub.server.app import db
from flask_login import current_user


class MachineManager(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MachineManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._machines = {}
            cls._instance.search()
        return cls._instance

    def __contains__(self, machine):
        if machine in self._machines.keys():
            return True
        else:
            return False

    def search(self):
        try:
            all_machines = [m.machinename for m in MachineModel.query.all()]
            machine_folders = [m for m in all_machines
                               if os.path.isdir(os.path.join(MACHINES_FOLDER, m))]

            for name in machine_folders:
                try:
                    machinefile = os.path.join(MACHINES_FOLDER, name, MACHINEFILE)
                    readme = os.path.join(MACHINES_FOLDER, name, 'readme.md')
                    if os.path.exists(machinefile):
                        doc, inputs = load_machinefile(machinefile)
                        readme_text = None
                        if os.path.exists(readme):
                            with open(readme, 'r') as f:
                                readme_text = f.read()
                        self._machines[name] = {'doc': doc,
                                                'inputs': inputs,
                                                'readme': readme_text}
                        create_image(name, [], [])
                except NotMachineHub:
                    continue
        except:
            pass

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

    def readme(self, name):
        try:
            machine = self._machines[name]
            return machine['readme']
        except:
            raise NotFoundException()

    def machines(self, names):
        try:
            info = []
            for name in names:
                info.append((name, self._machines[name]['doc']))
            return info
        except:
            raise NotFoundException()

    def delete(self, name):
        if os.path.exists(os.path.join(MACHINES_FOLDER, name)):
            shutil.rmtree(os.path.join(MACHINES_FOLDER, name))
        try:
            del self._machines[name]
        except:
            pass

    def _add(self, name, machinefile_path):
        out_folder = os.path.join(MACHINES_FOLDER, name, MACHINESOUT)
        doc, inputs = load_machinefile(machinefile_path)
        if os.path.exists(out_folder) and name in self._machines.keys():
            shutil.rmtree(out_folder)
        readme = os.path.join(MACHINES_FOLDER, name, 'readme.md')
        readme_text = None
        if os.path.exists(readme):
            with open(readme, 'r') as f:
                readme_text = f.read()
        self._machines[name] = {'doc': doc,
                                'inputs': inputs,
                                'readme': readme_text}
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
        create_image(name, [], [])

    def get_machines_for_page(self, page, per_page):
        origin = per_page * (page - 1)
        end = origin + per_page
        machines = self._machines.keys()[origin:end] if self.count > origin + per_page \
            else list(self._machines.keys())[origin:]
        info = []
        for machine in machines:
            info.append((machine, self._machines[machine]['doc']))
        return info

    def get_last_machines(self):
        info = []
        origin = 0
        if self.count > 7:
            origin = self.count-8
        for machine in list(self._machines.keys())[origin:]:
            info.append((machine, self._machines[machine]['doc']))
        return info

    def work(self, values, name):
        machine_id = date_sha1()
        with open(os.path.join(MACHINES_FOLDER, name, 'input%s.json' % machine_id), 'w+') as f:
            f.write(json.dumps(values))
        dockerize(name, machine_id)
        os.remove(os.path.join(MACHINES_FOLDER, name, 'input%s.json' % machine_id))


class MachineModel(db.Model):
    __tablename__ = 'machines'
    id = db.Column('machines_id', db.Integer, primary_key=True)
    machinename = db.Column('machinename', db.String(100), unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __init__(self, machinename):
        self.machinename = machinename


def add_machine_to_user(name):
    if name not in [m.machinename for m in current_user.machines.all()]:
        machine = MachineModel(name)
        machine.user = current_user
        db.session.add(machine)
    db.session.commit()

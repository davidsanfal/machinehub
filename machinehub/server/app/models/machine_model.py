import os
from machinehub.config import MACHINES_FOLDER, MACHINESOUT, MACHINEFILE
from machinehub.common.errors import NotFoundException, NotMachineHub
import shutil
from machinehub.common.machinefile_loader import load_machinefile, MachineParser
import json
from machinehub.common.sha import date_sha1
from machinehub.docker.dockerizer import dockerize, create_image
from machinehub.server.app import db
from flask_login import current_user
from datetime import datetime


class MachineManager(object):

    def __contains__(self, machine):
        if machine in [m.machinename for m in MachineModel.query.all()]:
            return True
        else:
            return False

    @property
    def all_machines(self):
        info = []
        for machine in MachineModel.query.all():
            doc, _ = machine.info
            info.append((machine.machinename, doc))

    def update(self, machinefile_path, name):
        try:
            out_folder = os.path.join(MACHINES_FOLDER, name, MACHINESOUT)
            machinefile = load_machinefile(machinefile_path)
            if os.path.exists(out_folder):
                shutil.rmtree(out_folder)
            if name in [m.machinename for m in current_user.machines.all()]:
                machine = MachineModel.query.filter_by(machinename=name).first()
                db.session.delete(machine)
                db.session.commit()

            readme_path = os.path.join(MACHINES_FOLDER, name, 'readme.md')
            readme = None
            if os.path.exists(readme_path):
                with open(readme_path, 'r') as f:
                    readme = f.read()

            os.makedirs(out_folder)
            create_image(name, [], [])
            machine = MachineModel(name, machinefile, readme)
            machine.user = current_user
            db.session.add(machine)
            db.session.commit()

        except NotMachineHub:
            raise NotMachineHub()
        return name

    def machine(self, name):
        machine = MachineModel.query.filter_by(machinename=name).first()
        if not machine:
            raise NotFoundException()
        return machine.info

    def readme(self, name):
        try:
            machine = MachineModel.query.filter_by(machinename=name).first()
            return machine.readme
        except:
            raise NotFoundException()

    def machines(self, names):
        try:
            info = []
            for name in names:
                doc, _ = self.machine(name)
                info.append((name, doc))
            return info
        except:
            raise NotFoundException()

    def delete(self, name):
        if os.path.exists(os.path.join(MACHINES_FOLDER, name)):
            shutil.rmtree(os.path.join(MACHINES_FOLDER, name))
        machine = MachineModel.query.filter_by(machinename=name).first()
        db.session.delete(machine)
        db.session.commit()

    def get_machines_for_page(self, page, per_page):
        all_machines = MachineModel.query.order_by(MachineModel.machinename).all()
        origin = per_page * (page - 1)
        end = origin + per_page
        machines = all_machines[origin:end] if len(all_machines) > origin + per_page \
            else all_machines[origin:]
        info = []
        for machine in machines:
            doc, _ = machine.info
            info.append((machine.machinename, doc))
        return info, len(all_machines)

    def get_last_machines(self):
        all_machines = MachineModel.query.order_by(MachineModel.created_on).all()
        info = []
        origin = 0
        if len(all_machines) > 7:
            origin = len(all_machines)-8
        for machine in all_machines[origin:]:
            doc, _ = machine.info
            info.append((machine.machinename, doc))
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
    readme = db.Column('readme', db.String)
    machinefile = db.Column('machinefile', db.String)
    created_on = db.Column('created_on', db.DateTime)
    version = db.Column('version', db.Integer)

    def __init__(self, machinename, machinefile, readme):
        self.machinename = machinename
        self.machinefile = machinefile
        self.readme = readme
        self.created_on = datetime.utcnow()
        self.version = 1

    @property
    def info(self):
        info = MachineParser(self.machinefile)
        return info.doc, info.inputs


def add_machine_to_user(name):
    if name not in [m.machinename for m in current_user.machines.all()]:
        machine = MachineModel(name)
        machine.user = current_user
        db.session.add(machine)
    db.session.commit()

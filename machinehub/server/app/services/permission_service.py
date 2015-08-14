from flask_login import current_user
from machinehub.server.app.models.machine_model import MachineModel


def user_is_owner(machine_name):
    authoraize_user = False
    if current_user.is_authenticated():
        authoraize_user = machine_name in [m.machinename for m in current_user.machines.all()]
    return authoraize_user


def user_can_edit(name):
    if current_user.is_authenticated():
        all_machines = [m.machinename for m in MachineModel.query.all()]
        if name in all_machines and name not in current_user.machine_names:
            return False
        else:
            return True
    else:
        return False

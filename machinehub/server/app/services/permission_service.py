from flask_login import current_user


def user_is_owner(machine_name):
    authoraize_user = False
    if current_user.is_authenticated():
        authoraize_user = machine_name in [m.machinename for m in current_user.machines.all()]
    return authoraize_user


def user_can_edit(names):
    from machinehub.server.app.models.user_model import UserMachine
    if current_user.is_authenticated():
        all_machines = [m.machinename for m in UserMachine.query.all()]
        user_machines = [m.machinename for m in current_user.machines.all()]
        for name in names:
            if name in all_machines and name not in user_machines:
                return False
        return True
    else:
        return False

from flask.globals import request
import os
from flask_classy import route, FlaskView
from flask.templating import render_template
from machinehub.config import UPLOAD_FOLDER, MACHINES_FOLDER, MACHINESOUT
from machinehub.server.app.models.machine_model import MachineModel
from machinehub.server.app.controllers.form_generator import metaform
from machinehub.common.sha import dict_sha1
from flask_login import login_required, current_user


types = {'int': int,
         'float': float}


class MachineController(FlaskView):
    decorators = []
    route_prefix = '/machine/'
    route_base = '/'

    def __init__(self):
        self.machines_model = MachineModel()

    @route('/<machine_name>', methods=['GET'])
    def machine(self, machine_name):
        show_stl = False
        authoraize_user = self._user_is_owner(machine_name)
        if machine_name not in self.machines_model:
            return render_template('404.html'), 404
        doc, inputs = self.machines_model.machine(machine_name)
        form = metaform('Form_%s' % str(machine_name), inputs)(request.form)
        return render_template('machine/machine.html',
                               title=doc.title,
                               description=doc.description,
                               images=doc.images,
                               form=form,
                               show_stl=show_stl,
                               file_name="",
                               machine_name=machine_name,
                               authoraize_user=authoraize_user)

    @route('/<machine_name>', methods=['POST'])
    def post_machine(self, machine_name):
        show_stl = False
        authoraize_user = self._user_is_owner(machine_name)
        if machine_name not in self.machines_model:
            return render_template('404.html'), 404
        doc, inputs = self.machines_model.machine(machine_name)
        form = metaform('Form_%s' % str(machine_name), inputs)(request.form)
        file_url = ""

        if form.validate():
            values = {}
            for name, _type, _, _, _ in inputs:
                value = getattr(form, name)
                if types.get(_type, None):
                    values[name] = types[_type](value.data)
                else:
                    values[name] = value.data
            current_folder = os.getcwd()
            os.chdir(os.path.join(MACHINES_FOLDER, machine_name))
            file_name = '%s_%s.stl' % (machine_name, dict_sha1(values))
            file_url = os.path.join('machines', machine_name, MACHINESOUT, file_name)
            file_path = os.path.join(UPLOAD_FOLDER, file_url)
            if not os.path.exists(file_path) or not values:
                values['file_path'] = file_name
                self.machines_model.work(values, machine_name)
            os.chdir(current_folder)
            show_stl = True
        return render_template('machine/machine.html',
                               title=doc.title,
                               description=doc.description,
                               images=doc.images,
                               form=form,
                               show_stl=show_stl,
                               file_name=file_url,
                               machine_name=machine_name,
                               authoraize_user=authoraize_user)

    @route('/<machine_name>', methods=['DELETE'])
    @login_required
    def delete_machine(self, machine_name):
        if machine_name not in self.machines_model:
            return render_template('404.html'), 404
        authoraize_user = self._user_is_owner(machine_name)
        if authoraize_user:
            from machinehub.server.app.models.user_model import UserMachine
            from machinehub.server.app.webapp import db
            machine = UserMachine(machine_name)
            del machine
            db.session.commit()
            self.machines_model.delete(machine_name)

    def _user_is_owner(self, machine_name):
        authoraize_user = False
        if current_user.is_authenticated():
            authoraize_user = machine_name in [m.machinename for m in current_user.machines.all()]
        return authoraize_user

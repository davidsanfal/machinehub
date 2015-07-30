from flask.globals import request
import os
from flask_classy import route, FlaskView
from flask.templating import render_template
from machinehub.server.app.controllers.auth_controller import requires_auth
from machinehub.config import UPLOAD_FOLDER, MACHINES_FOLDER, MACHINESOUT
from machinehub.server.app.models.machine_model import MachineModel
from machinehub.server.app.controllers.form_generator import metaform
from machinehub.common.sha import dict_sha1


types = {'int': int,
         'float': float}


ALLOWED_EXTENSIONS = ['py', 'zip']


class MachineController(FlaskView):
    decorators = [requires_auth]
    route_prefix = '/machine/'
    route_base = '/'

    def __init__(self):
        self.machines_model = MachineModel()

    @route('/<machine_name>', methods=['GET'])
    def machine(self, machine_name):
        show_stl = False
        if machine_name not in self.machines_model:
            return render_template('404.html'), 404
        _, doc, inputs = self.machines_model.machine(machine_name)
        form = metaform('Form_%s' % str(machine_name), inputs)(request.form)
        return render_template('machine/machine.html',
                               title=doc.title,
                               description=doc.description,
                               images=doc.images,
                               form=form,
                               show_stl=show_stl,
                               file_name="",
                               machine_name=machine_name)

    @route('/<machine_name>', methods=['POST'])
    def post_machine(self, machine_name):
        show_stl = False
        if machine_name not in self.machines_model:
            return render_template('404.html'), 404
        fn, doc, inputs = self.machines_model.machine(machine_name)
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
            file_url = os.path.join('machines', machine_name, MACHINESOUT,
                                    '%s_%s.stl' % (machine_name, dict_sha1(values)))
            file_path = os.path.join(UPLOAD_FOLDER, file_url)
            if not os.path.exists(file_path) or not values:
                values['file_path'] = file_path
                fn(**values)
            os.chdir(current_folder)
            show_stl = True
        return render_template('machine/machine.html',
                               title=doc.title,
                               description=doc.description,
                               images=doc.images,
                               form=form,
                               show_stl=show_stl,
                               file_name=file_url,
                               machine_name=machine_name)

    @route('/<machine_name>', methods=['DELETE'])
    def delete_machine(self, machine_name):
        if machine_name not in self.machines_model:
            return render_template('404.html'), 404
        self.machines_model.delete(machine_name)

from flask.globals import request
import os
from flask_classy import route, FlaskView
from flask.templating import render_template
from machinehub.server.app.controllers.auth_controller import requires_auth
from machinehub.config import UPLOAD_FOLDER
from machinehub.server.app.models.machine_model import MachineModel
from machinehub.server.app.controllers.form_generator import metaform
from flask.helpers import flash


types = {'int': int,
         'float': float}


ALLOWED_EXTENSIONS = ['py']


class MachineController(FlaskView):
    decorators = [requires_auth]
    route_prefix = '/machine/'
    route_base = '/'

    def __init__(self):
        self.machines_model = MachineModel()

    @route('/<machine_name>', methods=['GET', 'POST'])
    def machine(self, machine_name):
        show_stl = False
        fn, doc, inputs = self.machines_model.machine(machine_name)
        form = metaform('Form_%s' % str(machine_name), inputs)(request.form)
        file_name = ""
        if request.method == 'POST' and form.validate():
            try:
                values = {}
                for name, _type, _, _, _ in inputs:
                    value = getattr(form, name)
                    if types.get(_type, None):
                        values[name] = types[_type](value.data)
                    else:
                        values[name] = value.data
                current_folder = os.getcwd()
                os.chdir(UPLOAD_FOLDER)
                file_name = fn(**values)
                os.chdir(current_folder)
                show_stl = True
            except Exception as e:
                flash('WARNING! %s' % e.message, 'warning')
        return render_template('machine/machine.html',
                               title=doc.title,
                               description=doc.description,
                               images=doc.images,
                               form=form,
                               show_stl=show_stl,
                               file_name=file_name,
                               machine_name=machine_name)

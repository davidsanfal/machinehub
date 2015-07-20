from flask.globals import request
import os
from flask_classy import route, FlaskView
from flask.templating import render_template
from machinehub.server.app.controllers.auth_controller import requires_auth
from machinehub.config import UPLOAD_FOLDER, MACHINES_FOLDER
from machinehub.server.app.models.machine_model import MachineModel
from machinehub.server.app.controllers.form_generator import metaform
from machinehub.sha import dict_sha1
from flask.helpers import flash
import json


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
        file_url = ""
        if request.method == 'POST' and form.validate():
            values = {}
            for name, _type, _, _, _ in inputs:
                value = getattr(form, name)
                if types.get(_type, None):
                    values[name] = types[_type](value.data)
                else:
                    values[name] = value.data
            current_folder = os.getcwd()
            os.chdir(os.path.join(MACHINES_FOLDER, machine_name))
            file_url = os.path.join('machines',
                                    machine_name,
                                    '%s_%s.stl' % (machine_name, dict_sha1(values)))
            file_path = os.path.join(UPLOAD_FOLDER, file_url)
            if not os.path.exists(file_path):
                values['file_path'] = file_path
#                 a = json.dumps(values)
#                 print type(a)
#                 print type(json.loads(a))
                try:
                    fn(**values)
                    show_stl = True
                except:
                    flash('There are somthing wrong in that machine. Try to contant with the creator',
                          category='danger')
                    show_stl = False
                finally:
                    os.chdir(current_folder)
            else:
                show_stl = True
        return render_template('machine/machine.html',
                               title=doc.title,
                               description=doc.description,
                               images=doc.images,
                               form=form,
                               show_stl=show_stl,
                               file_name=file_url,
                               machine_name=machine_name)

from flask.globals import request
import os
from flask_classy import route, FlaskView
from flask.templating import render_template
from machinehub.config import UPLOAD_FOLDER, MACHINES_FOLDER, MACHINESOUT
from machinehub.server.app.models.machine_model import MachineManager
from machinehub.server.app.utils.form_generator import metaform
from machinehub.common.sha import dict_sha1
from flask_login import login_required
from machinehub.server.app.services.permission_service import user_is_owner
from machinehub.common.errors import ForbiddenException
from machinehub.server.app import db
from machinehub.server.app.models.machine_model import MachineModel, add_machine_to_user
from machinehub.server.app.models.resources_model import upload_machine
from flask.helpers import url_for, flash
from werkzeug.utils import redirect


types = {'int': int,
         'float': float}


class MachineController(FlaskView):
    decorators = []
    route_prefix = '/machine/'
    route_base = '/'

    def __init__(self):
        self.machines_model = MachineManager()

    @route('/<machine_name>', methods=['GET'])
    def machine(self, machine_name):
        show_stl = False
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
                               authoraize_user=user_is_owner(machine_name))

    @route('/<machine_name>', methods=['POST'])
    def post_machine(self, machine_name):
        show_stl = False
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
                               authoraize_user=user_is_owner(machine_name))

    @route('/<machine_name>', methods=['DELETE'])
    @login_required
    def delete_machine(self, machine_name):
        if machine_name not in self.machines_model:
            return render_template('404.html'), 404
        if user_is_owner(machine_name):
            machine = MachineModel.query.filter_by(machinename=machine_name).first()
            db.session.delete(machine)
            db.session.commit()
            self.machines_model.delete(machine_name)
        return '', 200

    @route('/new', methods=['GET', 'POST'])
    @login_required
    def new(self):
        if request.method == 'POST':
            uploaded_files = request.files.getlist("file[]")
            try:
                machines = []
                for uploaded_file in uploaded_files:
                    name = upload_machine(uploaded_file, self.machines_model)
                    if name:
                        add_machine_to_user(name)
                        machines.append(name)
                if len(machines) == 1:
                    return redirect(url_for('MachineController:machine', machine_name=machines[0]))
                elif len(machines) >= 1:
                    return redirect(url_for('MachinehubController:index'))
                else:
                    flash('Machines not found', 'warning')
            except ForbiddenException as e:
                flash(e.message, 'warning')
        return render_template('machine/upload.html')

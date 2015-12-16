from machinehub.server.rest.controllers.controller import Controller
from bottle import request
from machinehub.errors import NotFoundException
import json
import os
from machinehub.common.sha import dict_sha1
from machinehub.config import MACHINESOUT, MACHINES_FOLDER, UPLOAD_FOLDER
from machinehub.server.rest.models.resources_model import upload_machine

types = {'int': int,
         'float': float}


class MachinehubController(Controller):
    """
        Serve requests related with Machinehub
    """
    def attach_to(self, app):

        machine_route = '%s/:username/:machinename' % self.route

        # FIXME: REPLACE ROUTE WITH AN ER COMPOSED WITH ERs for
        # {machinename}/{version}/{username}

        @app.route("%s" % machine_route, methods=['GET'])
        def machine(self, username, machinename, auth_user):
            machine_name = os.path.join(username, machinename)
            if machine_name not in self.machines_manager:
                raise NotFoundException
            doc, inputs = self.machines_manager.machine(machine_name)
            readme = self.machines_manager.readme(machine_name)
            return json.loads({'info': doc,
                               'inputs': inputs,
                               'readme': readme,
                               'machine_name': machine_name,
                               'authoraize_user': username == auth_user})

        @app.route("%s" % machine_route, methods=['POST'])
        def post_machine(self, username, machinename, auth_user):
            machine_name = os.path.join(username, machinename)
            if machine_name not in self.machines_manager:
                raise NotFoundException
            _, inputs = self.machines_manager.machine(machine_name)
            values = {}
            parameters = json.dumps(request.json)
            for name, _type, _, _, _ in inputs:
                value = parameters[name]
                if types.get(_type, None):
                    values[name] = types[_type](value.data)
                else:
                    values[name] = value.data
            current_folder = os.getcwd()
            os.chdir(os.path.join(MACHINES_FOLDER, machine_name))
            file_name = '%s_%s.stl' % (machine_name.replace('/', '_'), dict_sha1(values))
            file_url = os.path.join('machines', machine_name, MACHINESOUT, file_name)
            file_path = os.path.join(UPLOAD_FOLDER, file_url)
            if not os.path.exists(file_path) or not values:
                values['file_path'] = file_name
                self.machines_manager.work(values, machine_name)
            os.chdir(current_folder)
            return json.loads({'file_name': file_url,
                               'machine_name': machine_name,
                               'authoraize_user': username == auth_user})

        @app.route("%s" % machine_route, methods=['DELETE'])
        def delete_machine(self, username, machinename, auth_user):
            machine_name = os.path.join(username, machinename)
            if machine_name not in self.machines_manager:
                raise NotFoundException
            app.authoraizer.user_is_owner(username)
            self.machines_manager.delete(machine_name)

        @app.route("%s/new" % self.route, methods=['POST'])
        def new(self):
            uploaded_files = request.files.getlist("file[]")
            for uploaded_file in uploaded_files:
                upload_machine(uploaded_file, self.machines_manager)

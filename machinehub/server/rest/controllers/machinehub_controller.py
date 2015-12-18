from machinehub.server.rest.controllers.controller import Controller
from bottle import request, FileUpload
import os
from machinehub.config import MACHINESOUT, MACHINES_FOLDER, UPLOAD_FOLDER
from machinehub.sha import dict_sha1
from machinehub.server.service.machine_service import MachineManager

types = {'int': int,
         'float': float}


class MachinehubController(Controller):
    """
        Serve requests related with Machinehub
    """

    def attach_to(self, app):
        machines_manager = MachineManager(app.authorizer)

        machine_route = '%s/:username/:machinename' % self.route

        # FIXME: REPLACE ROUTE WITH AN ER COMPOSED WITH ERs for
        # {machinename}/{username}

        @app.route("%s" % machine_route, method=['GET'])
        def machine(username, machinename, auth_user):
            machine_name = os.path.join(username, machinename)
            return {'info': 'hola caracola',
                    'inputs': {'a': 'cosas',
                               'b': 'cosas'},
                    'readme': 'readme',
                    'machine_name': machine_name,
                    'authoraize_user': username == auth_user}

        @app.route("%s" % machine_route, method=['POST'])
        def post_machine(username, machinename, auth_user):
            machine_name = os.path.join(username, machinename)
            data = request.json
            # current_folder = os.getcwd()
            # os.chdir(os.path.join(MACHINES_FOLDER, machine_name))
            file_name = '%s_%s.stl' % (machine_name.replace('/', '_'), dict_sha1())
            file_url = os.path.join('machines', machine_name, MACHINESOUT, file_name)
            file_path = os.path.join(UPLOAD_FOLDER, file_url)
            # os.chdir(current_folder)
            return {'file_name': file_url,
                    'machine_name': machine_name,
                    'authoraize_user': username == auth_user}

        @app.route("%s" % machine_route, method=['DELETE'])
        def delete_machine(username, machinename, auth_user):
            machine_name = os.path.join(username, machinename)
            app.authorizer.user_is_owner(auth_user, username)

        @app.route(self.route, method=['PUT'])
        def new(auth_user):
            uploaded_file = request.files.get("fileUpload")
            machines_manager.new(uploaded_file, auth_user)

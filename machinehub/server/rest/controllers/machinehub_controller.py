from machinehub.server.rest.controllers.controller import Controller
from bottle import request, static_file, response
import os
from machinehub.server.service.machine_service import MachineManager
from machinehub.config import MACHINES_FOLDER, MACHINESOUT
import mimetypes


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
            machinefile, readme = machines_manager.read(machine_name)
            inputs = {}
            for name, _type, default, _range, allowed_values in machinefile.inputs:
                inputs[name] = {'type': _type,
                                'default': default,
                                'range': _range,
                                'allowed_values': allowed_values}
            return {'info': {'title': machinefile.doc.title,
                             'description':  machinefile.doc.description},
                    'inputs': inputs,
                    'readme': readme,
                    'machine_name': machine_name,
                    'authoraize_user': username == auth_user}

        @app.route("%s" % machine_route, method=['POST'])
        def use_machine(username, machinename, auth_user):
            machine_name = os.path.join(username, machinename)
            file_url = machines_manager.work(machine_name, request.json)
            return {'file_url': file_url,
                    'machine_name': machine_name,
                    'authoraize_user': username == auth_user}

        @app.route("%s/<filepath:path>" % machine_route, method=['GET'])
        def download_file(username, machinename, filepath, auth_user):
            complete_filepath = os.path.join(MACHINES_FOLDER, username,
                                             machinename,
                                             MACHINESOUT,
                                             filepath)
            # https://github.com/kennethreitz/requests/issues/1586
            mimetype = "x-gzip" if complete_filepath.endswith(".tgz") else "auto"
            return static_file(os.path.basename(complete_filepath),
                               root=os.path.dirname(complete_filepath),
                               mimetype=mimetype)

        @app.route("%s" % machine_route, method=['DELETE'])
        def delete_machine(username, machinename, auth_user):
            machine_name = os.path.join(username, machinename)
            app.authorizer.user_is_owner(auth_user, username)
            machines_manager.delete(machine_name)

        @app.route(self.route, method=['PUT'])
        def new(auth_user):
            uploaded_file = request.files.get("fileUpload")
            if machines_manager.new(uploaded_file, auth_user):
                return {'status': 'success'}

from flask import Flask
from flask.helpers import url_for
from machinehub.config import UPLOAD_FOLDER
from flask import request
from machinehub.server.app.controllers.machine_controller import MachineController
from machinehub.server.app.controllers.machinehub_controller import MachinehubController
from machinehub.server.app.models.machine_model import MachineModel


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


machine_model = MachineModel()
app = Flask(__name__)
app.secret_key = 'development key'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.jinja_env.globals['url_for_other_page'] = url_for_other_page

MachinehubController().register(app)
MachineController().register(app)

if UPLOAD_FOLDER:
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

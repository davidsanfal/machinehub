from flask import Flask
from flask.helpers import url_for
from machinehub.config import UPLOAD_FOLDER
from flask import request
from machinehub.server.app.controllers.machine_controller import MachineController
from machinehub.server.app.controllers.machinehub_controller import MachinehubController
from flask import render_template
import flask


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


app = Flask(__name__)
app.secret_key = 'development key'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.before_request
def before_request():
    method = request.form.get('_method', '').upper()
    if method:
        request.environ['REQUEST_METHOD'] = method
        ctx = flask._request_ctx_stack.top
        ctx.url_adapter.default_method = method
        assert request.method == method


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


app.jinja_env.globals['url_for_other_page'] = url_for_other_page

MachinehubController().register(app)
MachineController().register(app)

if UPLOAD_FOLDER:
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

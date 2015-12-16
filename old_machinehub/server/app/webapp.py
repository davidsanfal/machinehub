from flask.helpers import url_for
from old_machinehub.server.app.controllers.machine_controller import MachineController
from old_machinehub.server.app.controllers.machinehub_controller import MachinehubController
from flask.templating import render_template
from old_machinehub.server.app.controllers.auth_controller import AuthController
from werkzeug.utils import redirect
from old_machinehub.server.app.controllers.user_controller import UserController
from old_machinehub.server.app import app


UserController().register(app)
MachinehubController().register(app)
MachineController().register(app)
AuthController().register(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(401)
def unauthorized(e):
    return redirect(url_for('AuthController:login'))


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

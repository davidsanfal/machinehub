from flask import Flask
from flask.helpers import url_for
from machinehub.config import UPLOAD_FOLDER
from flask import request
from machinehub.server.app.controllers.machine_controller import MachineController
from machinehub.server.app.controllers.machinehub_controller import MachinehubController
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask.templating import render_template
from machinehub.server.app.controllers.auth_controller import AuthController
from werkzeug.utils import redirect


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


app = Flask(__name__)
app.secret_key = 'development key'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/users.db'
if UPLOAD_FOLDER:
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.jinja_env.globals['url_for_other_page'] = url_for_other_page

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

MachinehubController().register(app)
MachineController().register(app)
AuthController().register(app)


@login_manager.user_loader
def load_user(id):
    from machinehub.server.app.models.user_model import User
    return User.query.get(int(id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(401)
def unauthorized(e):
    return redirect(url_for('AuthController:login'))


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

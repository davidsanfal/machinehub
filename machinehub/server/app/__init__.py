from flask import Flask
from machinehub.config import UPLOAD_FOLDER
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import request
from flask.helpers import url_for


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

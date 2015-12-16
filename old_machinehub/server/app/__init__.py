from flask import Flask
from old_machinehub.config import BaseConfig
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import request
from flask.helpers import url_for
from flask_mail import Mail
import os


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)

app = Flask(__name__)

app.config.from_object(BaseConfig)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page

mail = Mail(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

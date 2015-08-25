from flask import Flask
from machinehub.config import UPLOAD_FOLDER
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import request
from flask.helpers import url_for
from flask_mail import Mail
import os


class BaseConfig(object):
    """Base configuration."""

    # main config
    SECRET_KEY = 'development key'
    SECURITY_PASSWORD_SALT = 'the_power_of_the_unicorns'
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SEND_FILE_MAX_AGE_DEFAULT = 0
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/users.db'
    UPLOAD_FOLDER = UPLOAD_FOLDER

    # mail settings
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # gmail authentication
    MAIL_USERNAME = os.environ['APP_MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['APP_MAIL_PASSWORD']

    # mail accounts
    MAIL_DEFAULT_SENDER = 'from@example.com'


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

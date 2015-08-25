import os
from machinehub.config.config_parser import ConfigParser
import logging
from machinehub.config.env_reader import get_env
import sys

MACHINEHUB = '.machinehub'
MACHINEHUBCONF = 'machinehub.conf'
MACHINESOUT = 'machine_out'
MACHINEFILE = 'machinefile.txt'
default_machinehubconf = '''
[server]
host: 127.0.0.1
port: 5000
[users]
admin: admin
'''

machinehub_path = os.path.join(os.path.expanduser('~'), MACHINEHUB)
UPLOAD_FOLDER = machinehub_path
MACHINES_FOLDER = os.path.join(UPLOAD_FOLDER, 'machines')
if not os.path.exists(MACHINES_FOLDER):
    os.makedirs(MACHINES_FOLDER)
sys.path.append(MACHINES_FOLDER)
machinehubconfig_path = os.path.join(machinehub_path, MACHINEHUBCONF)
config = None
if not os.path.exists(machinehubconfig_path):
    if not os.path.exists(machinehub_path):
        os.makedirs(machinehub_path)
    with open(machinehubconfig_path, "w+") as f:
        f.write(default_machinehubconf)

with open(machinehubconfig_path, "r") as f:
    config = f.read()

machinehub_conf = ConfigParser(config, ['server', 'users'])


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
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/users.db' % machinehub_path
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

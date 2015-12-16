import os
from machinehub.config.config_parser import ConfigParser
import logging
from machinehub.config.env_reader import get_env
import sys

MACHINEHUB = '.old_machinehub'
MACHINEHUBCONF = 'old_machinehub.conf'
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
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/old_machinehub.db' % machinehub_path
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

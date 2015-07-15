import os
from machinehub.config.config_parser import ConfigParser
import logging
from machinehub.config.env_reader import get_env
import sys

MACHINEHUB = '.machinehub'
MACHINEHUBCONF = 'machinehub.conf'
default_machinehubconf = '''
[server]
host: 127.0.0.1
port: 5000
[users]
admin: admin
'''

machinehub_path = os.path.join(os.path.expanduser('~'), MACHINEHUB)
UPLOAD_FOLDER = machinehub_path
MACHINEHUB_FOLDER = os.path.join(UPLOAD_FOLDER, 'machines')
if not os.path.exists(MACHINEHUB_FOLDER):
    os.makedirs(MACHINEHUB_FOLDER)
sys.path.append(MACHINEHUB_FOLDER)
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

# #### LOGGER #####
MACHINEHUB_LOGGING_LEVEL = get_env('MACHINEHUB_LOGGING_LEVEL', logging.CRITICAL)
MACHINEHUB_LOGGING_FILE = get_env('MACHINEHUB_LOGGING_FILE', None)  # None is stdout

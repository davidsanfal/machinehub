#!/usr/bin/python3
from machinehub.server.service.authorize import BasicAuthorizer, BasicAuthenticator
from machinehub.server.conf import get_file_manager
from machinehub.server.rest.server import MachinehubServer
from machinehub.server.crypto.jwt.jwt_credentials_manager import JWTCredentialsManager
from machinehub.server.crypto.jwt.jwt_updown_manager import JWTUpDownAuthManager
import os

from machinehub.server.conf import ConanServerConfigParser


def get_server_config(base_folder, storage_folder=None):
    server_config = ConanServerConfigParser(base_folder, storage_folder=storage_folder)
    return server_config


class ServerLauncher(object):
    def __init__(self):
        user_folder = os.path.expanduser("~")

        server_config = get_server_config(user_folder)

        authorizer = BasicAuthorizer(server_config.read_permissions,
                                     server_config.write_permissions)
        authenticator = BasicAuthenticator(dict(server_config.users))

        credentials_manager = JWTCredentialsManager(server_config.jwt_secret,
                                                    server_config.jwt_expire_time)

        updown_auth_manager = JWTUpDownAuthManager(server_config.updown_secret,
                                                   server_config.authorize_timeout)

        file_manager = get_file_manager(server_config, updown_auth_manager=updown_auth_manager)

        self.ra = MachinehubServer(server_config.port, server_config.ssl_enabled,
                                   credentials_manager, updown_auth_manager,
                                   authorizer, authenticator, file_manager)

    def launch(self):
        self.ra.run(host="0.0.0.0")


launcher = ServerLauncher()
app = launcher.ra.root_app


def main(*args):
    launcher.launch()


if __name__ == "__main__":
    main()

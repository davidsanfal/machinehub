#!/usr/bin/python3
from machinehub.server.service.authorize import BasicAuthorizer, BasicAuthenticator
from machinehub.server.rest.server import MachinehubServer
from machinehub.server.crypto.jwt.jwt_credentials_manager import JWTCredentialsManager
from datetime import timedelta
from machinehub.config import machinehub_conf


class ServerLauncher():
    def __init__(self, users=None):
        authorizer = BasicAuthorizer()
        users = users or {}
        authenticator = BasicAuthenticator(users)
        credentials_manager = JWTCredentialsManager("unicornio_rosa", timedelta(minutes=121))

        self.ra = MachinehubServer(machinehub_conf.server.port, False, credentials_manager, authorizer, authenticator)

    def launch(self):
        self.ra.run(host=machinehub_conf.server.host)


launcher = ServerLauncher(machinehub_conf.users._sections)
app = launcher.ra.root_app


def main(*args):
    launcher.launch()


if __name__ == "__main__":
    main()

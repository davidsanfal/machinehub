#!/usr/bin/python3
from machinehub.server.service.authorize import BasicAuthorizer, BasicAuthenticator
from machinehub.server.rest.server import MachinehubServer
from machinehub.server.crypto.jwt.jwt_credentials_manager import JWTCredentialsManager
from datetime import timedelta


class ServerLauncher():
    def __init__(self):
        authorizer = BasicAuthorizer()
        users = {'admin': 'pass'}
        authenticator = BasicAuthenticator(users)
        credentials_manager = JWTCredentialsManager("unicornio_rosa", timedelta(minutes=121))

        self.ra = MachinehubServer(5505, False, credentials_manager, authorizer, authenticator)

    def launch(self):
        self.ra.run(host="0.0.0.0")


launcher = ServerLauncher()
app = launcher.ra.root_app


def main(*args):
    launcher.launch()


if __name__ == "__main__":
    main()

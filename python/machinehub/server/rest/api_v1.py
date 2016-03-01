from bottle import Bottle
from machinehub.server.rest.bottle_plugins.non_ssl_blocker import NonSSLBlocker
from machinehub.server.rest.bottle_plugins.http_basic_authentication import HttpBasicAuthentication
from machinehub.server.rest.bottle_plugins.jwt_authentication import JWTAuthentication
from machinehub.server.rest.bottle_plugins.return_handler import ReturnHandlerPlugin
from machinehub.errors import EXCEPTION_CODE_MAPPING
from machinehub.server.rest.controllers.users_controller import UsersController
from machinehub.server.rest.controllers.machinehub_controller import MachinehubController


class ApiV1(Bottle):

    def __init__(self, credentials_manager, ssl_enabled, *argc, **argv):
        self.credentials_manager = credentials_manager
        self.ssl_enabled = ssl_enabled
        Bottle.__init__(self, *argc, **argv)

    def setup(self):
        self.install_plugins()
        # Install machinehub controller
        MachinehubController("/machine").attach_to(self)
        # Install users controller
        UsersController("/users").attach_to(self)

    def install_plugins(self):
        # Very first of all, check SSL or die
        if self.ssl_enabled:
            self.install(NonSSLBlocker())

        # Second, check Http Basic Auth
        self.install(HttpBasicAuthentication())

        # Map exceptions to http return codes
        self.install(ReturnHandlerPlugin(EXCEPTION_CODE_MAPPING))

        # Handle jwt auth
        self.install(JWTAuthentication(self.credentials_manager))

from bottle import Bottle
from machinehub.server.rest.bottle_plugins.non_ssl_blocker import NonSSLBlocker
from machinehub.server.rest.bottle_plugins.http_basic_authentication import HttpBasicAuthentication
from machinehub.server.rest.bottle_plugins.jwt_authentication import JWTAuthentication
from machinehub.server.rest.bottle_plugins.return_handler import ReturnHandlerPlugin
from machinehub.errors import EXCEPTION_CODE_MAPPING
from machinehub.server.rest.controllers.conan_controller import MachinehubController
from machinehub.server.rest.controllers.users_controller import UsersController
from machinehub.server.rest.controllers.file_upload_download_controller import FileUploadDownloadController


class ApiV1(Bottle):

    def __init__(self, credentials_manager, updown_auth_manager,
                 ssl_enabled, server_version, *argc, **argv):
        self.credentials_manager = credentials_manager
        self.updown_auth_manager = updown_auth_manager
        self.ssl_enabled = ssl_enabled
        self.server_version = server_version
        Bottle.__init__(self, *argc, **argv)

    def setup(self):
        self.install_plugins()
        # Install machinehub controller
        MachinehubController("/machinehub").attach_to(self)
        # Install users controller
        UsersController("/users").attach_to(self)
        # Install updown controller
        if self.updown_auth_manager:
            FileUploadDownloadController("/files").attach_to(self)

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

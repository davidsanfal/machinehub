#!/usr/bin/python3
from machinehub.server.service.authorize import BasicAuthorizer, BasicAuthenticator
import os
from machinehub.server.rest.server import MachinehubServer
from machinehub.server.crypto.jwt.jwt_credentials_manager import JWTCredentialsManager
from machinehub.util.log import logger
from machinehub.util.files import mkdir
import tempfile
from _datetime import timedelta


MACHINEHUB_TEST_FOLDER = os.getenv('MACHINEHUB_TEST_FOLDER', None)


def temp_folder():
    t = tempfile.mkdtemp(suffix='conans', dir=MACHINEHUB_TEST_FOLDER)
    nt = os.path.join(t, "path with spaces")
    os.makedirs(nt)
    return nt


TESTING_REMOTE_PRIVATE_USER = "private_user"
TESTING_REMOTE_PRIVATE_PASS = "private_pass"


class TestServerLauncher():
    port = 0

    def __init__(self, base_path=None, users=None, base_url=None, plugins=None):

        plugins = plugins or []
        if not base_path:
            base_path = temp_folder()

        if not os.path.exists(base_path):
            raise Exception("Base path not exist! %s")

        # Define storage_folder, if not, it will be readed from conf file and pointed to real user home
        storage_folder = os.path.join(base_path, ".machinehub", "data")
        mkdir(storage_folder)

        if TestServerLauncher.port == 0:
            TestServerLauncher.port = 5505

        if not users:
            users = {'admin': 'pass'}

        users[TESTING_REMOTE_PRIVATE_USER] = TESTING_REMOTE_PRIVATE_PASS

        authorizer = BasicAuthorizer()
        authenticator = BasicAuthenticator(users)
        credentials_manager = JWTCredentialsManager("unicorn_test", timedelta(minutes=121))

        logger.debug("Storage path: %s" % storage_folder)
        self.port = TestServerLauncher.port
        TestServerLauncher.port += 1
        self.ra = MachinehubServer(self.port, False, credentials_manager, authorizer, authenticator)
        for plugin in plugins:
            self.ra.api_v1.install(plugin)

    def start(self, daemon=True):
        """from multiprocessing import Process
        self.p1 = Process(target=ra.run, kwargs={"host": "0.0.0.0"})
        self.p1.start()
        self.p1"""
        import threading
        self.t1 = threading.Thread(target=self.ra.run, kwargs={"host": "0.0.0.0"})
        self.t1.daemon = daemon
        self.t1.start()

    def stop(self):
        self.ra.root_app.close()


if __name__ == "__main__":
    server = TestServerLauncher()
    server.start(daemon=False)

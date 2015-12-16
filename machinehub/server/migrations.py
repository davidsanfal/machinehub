from machinehub.migrations import Migrator
from machinehub.model.version import Version
from machinehub.util.files import rmdir


class ServerMigrator(Migrator):

    def _make_migrations(self, old_version):
        # ############### FILL THIS METHOD WITH THE REQUIRED ACTIONS ##############

        # VERSION 0.1
        if old_version == Version("0.1"):
            # Remove config, machinehub, all!
            self.out.warn("Reseting configuration and storage files...")
            if self.conf_path:
                rmdir(self.conf_path)
            if self.store_path:
                rmdir(self.store_path)

        # ########################################################################

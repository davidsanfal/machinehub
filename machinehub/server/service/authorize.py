'''

This module handles user authentication and permissions
for read or write a machinehub or package.

This only reads from file the users and permissions.

Replace this module with other that keeps the interface or super class.

'''


from abc import ABCMeta, abstractmethod
from machinehub.errors import ForbiddenException

#  ############################################
#  ############ ABSTRACT CLASSES ##############
#  ############################################


class Authorizer(object):
    """
    Handles the access permissions to machinehub and packages
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def check_read_conan(self, username, conan_reference):
        """
        username: User that request to read the machinehub
        conan_reference: ConanFileReference
        """
        raise NotImplemented()

    @abstractmethod
    def check_write_conan(self, username, conan_reference):
        """
        username: User that request to write the machinehub
        conan_reference: ConanFileReference
        """
        raise NotImplemented()

    @abstractmethod
    def check_read_package(self, username, package_reference):
        """
        username: User that request to read the package
        package_reference: PackageReference
        """
        raise NotImplemented()

    @abstractmethod
    def check_write_package(self, username, package_reference):
        """
        username: User that request to write the package
        package_reference: PackageReference
        """
        raise NotImplemented()


class Authenticator(object):
    """
    Handles the user authentication
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def valid_user(self, username, plain_password):
        """
        username: User that request to read the machinehub
        conan_reference: ConanFileReference
        """
        raise NotImplemented()

#  ########################################################
#  ############ BASIC IMPLEMENTATION CLASSES ##############
#  ########################################################


class BasicAuthenticator(Authenticator):
    """
    Handles the user authentication from a dict of plain users and passwords.
    users is {username: plain-text-passwd}
    """

    def __init__(self, users):
        self.users = users

    def valid_user(self, username, plain_password):
        """
        username: User that request to read the machinehub
        conan_reference: ConanFileReference
        return: True if match False if don't
        """
        return username in self.users and self.users[username] == plain_password


class BasicAuthorizer(Authorizer):
    """
    Reads permissions from the config file (server.cfg)
    """

    def __init__(self, read_permissions, write_permissions):
        """List of tuples with conanrefernce and users:

        [(conan_reference, "user, user, user"),
         (conan_reference2, "user3, user, user")] """

        self.read_permissions = read_permissions
        self.write_permissions = write_permissions

    def user_is_owner(self, username, machine_user):

        if machine_user.user == username:
            return
        raise ForbiddenException("Unauthorized")


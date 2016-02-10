'''

This module handles user authentication and permissions
for read or write a machines.

This only reads from file the users and permissions.

Replace this module with other that keeps the interface or super class.

'''


from abc import ABCMeta, abstractmethod
from machinehub.errors import ForbiddenException

#  ############################################
#  ############ ABSTRACT CLASSES ##############
#  ############################################


class Authorizer():

    __metaclass__ = ABCMeta

    @abstractmethod
    def user_is_owner(self, username, machine_user):

        raise NotImplemented()

    @abstractmethod
    def user_can_edit(self, username, machine_user):

        raise NotImplemented()


class Authenticator(object):
    """
    Handles the user authentication
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def valid_user(self, username, plain_password):

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
        return username in self.users and self.users[username] == plain_password


class BasicAuthorizer(Authorizer):
    """
    Reads permissions
    """

    def user_is_owner(self, username, machine):
        user, _ = machine.split('/')
        if user == username:
            return
        raise ForbiddenException("Unauthorized")

    def user_can_edit(self, username, machine):
        return self.user_is_owner(username, machine)

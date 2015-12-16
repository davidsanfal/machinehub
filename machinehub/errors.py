'''
    Exceptions raised and handled in Conan server.
    These exceptions are mapped between server (as an HTTP response) and client
    through the REST API. When an error happens in server its translated to an HTTP
    error code that its sent to client. Client reads the server code and raise the
    matching exception.

    see return_plugin.py

'''


class MachinehubException(Exception):
    """
         Generic machinehub exception
    """
    pass


class InternalErrorException(MachinehubException):
    """
         Generic 500 error
    """
    pass


class RequestErrorException(MachinehubException):
    """
         Generic 400 error
    """
    pass


class AuthenticationException(MachinehubException):  # 401
    """
        401 error
    """
    pass


class ForbiddenException(MachinehubException):  # 403
    """
        403 error
    """
    pass


class NotFoundException(MachinehubException):  # 404
    """
        404 error
    """
    pass


class UserInterfaceErrorException(RequestErrorException):
    """
        420 error
    """
    pass


EXCEPTION_CODE_MAPPING = {InternalErrorException: 500,
                          RequestErrorException: 400,
                          AuthenticationException: 401,
                          ForbiddenException: 403,
                          NotFoundException: 404,
                          UserInterfaceErrorException: 420}

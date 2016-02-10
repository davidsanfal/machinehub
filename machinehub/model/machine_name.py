from machinehub.errors import InvalidNameException
from machinehub.model.complex_name import ComplexName
from machinehub.model.user_name import UserName


class MachineName(str):

    def __new__(cls, name, validate=True):
        if not validate:
            obj = str.__new__(cls, name)
        else:
            original_name = name
            try:
                name = name.strip().replace('\\', '/')
                tokens = name.split('/')
                if '' in tokens:
                    raise InvalidNameException('%s is not a valid %s. It has trailing slashes'
                                               % (name, cls.__name__))
                if len(tokens) > 2:
                    raise InvalidNameException('%s is not a valid %s. '
                                               'It should be in the form user/name'
                                               % (name, cls.__name__))
                user = tokens[0]
                obj = str.__new__(cls, user + '/' + tokens[1])
                obj._name = ComplexName(tokens[1])
                obj._user = UserName(user)
            except IndexError:
                raise InvalidNameException('%s is not a valid %s' % (original_name, cls.__name__))
        return obj

    def _parse(self):
        tokens = self.split('/', 1)
        self._user = UserName(tokens[0], False)
        self._name = ComplexName(tokens[1], False)

    @property
    def user(self):
        try:
            return self._user
        except:
            self._parse()
            return self._user

    @property
    def name(self):
        try:
            return self._name
        except:
            self._parse()
            return self._name

    def serialize(self):
        return self[:]

    @staticmethod
    def deserialize(data):
        return MachineName(data, False)

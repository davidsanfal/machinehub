import re
from machinehub.common.errors import MachinehubException


class ConfigParser(object):
    def __init__(self, text, allowed_fields=None):
        self._sections = {}
        self._allowed_fields = allowed_fields or []
        pattern = re.compile("^\[([a-z_]{2,50})\]")
        current_lines = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line[0] == '#':
                continue
            m = pattern.match(line)
            if m:
                group = m.group(1)
                if self._allowed_fields and group not in self._allowed_fields:
                    raise MachinehubException("ConfigParser: Unrecognized field '%s'" % group)
                current_lines = []
                self._sections[group] = current_lines
            else:
                current_lines.append(line)

    def __getattr__(self, name):
        if name in self._sections:
            return ConfigSection(name, "\n".join(self._sections[name]))
        else:
            if self._allowed_fields and name in self._allowed_fields:
                return ""
            else:
                raise MachinehubException("ConfigParser: Unrecognized field '%s'" % name)


class ConfigSection(object):

    def __init__(self, name, text):
        self.name = name
        self._sections = {}
        for line in text.splitlines():
            key, value = line.split(':', 1)
            value = value.replace(' ', '') if value.startswith(' ') else value
            if self._allowed_fields and key not in self._allowed_fields:
                raise MachinehubException("%s config: Unrecognized field '%s'" % (self.name, key))
            self._sections[key] = value

    def __getattr__(self, key):
        if key in self._sections:
            return self._sections[key]
        return None

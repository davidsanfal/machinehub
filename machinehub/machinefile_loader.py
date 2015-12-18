from old_machinehub.common.errors import MachinehubException
import os
import re


def load_machinefile(machinefile_path):
    """ loads a machinefile from the given file
    """

    if not os.path.exists(machinefile_path):
        raise MachinehubException("%s not found!" % machinefile_path)
    try:
        with open(machinefile_path, 'r') as f:
            machinefile = f.read()
            machinefile = MachineParser(machinefile)
            return machinefile
    except MachinehubException as e:  # re-raise with file name
        raise MachinehubException("%s: %s" % (machinefile_path, str(e)))


class MachineParser(object):
    def __init__(self, text):
        self.doc = None
        self.inputs = None
        doc_lines = []
        inputs_lines = []
        outputs_lines = []
        sysdeps_lines = []
        engines_lines = []
        pattern = re.compile("^\[([a-z_]{2,50})\]")
        current_lines = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line[0] == '#':
                continue
            m = pattern.match(line)
            if m:
                group = m.group(1)
                current_lines = []
                if group == 'doc':
                    doc_lines = current_lines
                elif group == 'inputs':
                    inputs_lines = current_lines
                elif group == 'outputs':
                    outputs_lines = current_lines
                elif group == 'sysdeps':
                    sysdeps_lines = current_lines
                elif group == 'engines':
                    engines_lines = current_lines
                else:
                    raise MachinehubException("MachineParser: Unrecognized field '%s'" % group)
            else:
                current_lines.append(line)
        self.doc = DocMachine(doc_lines)
        self.inputs = InputsMachine(inputs_lines).inputs
        self.outputs = OutputsMachine(outputs_lines).extensions
        _sysdeps = DepsMachine(sysdeps_lines)
        self.sysdeps, self.pipdeps = _sysdeps.sysdeps, _sysdeps.pip
        _engines = EnginesMachine(engines_lines)
        self.engine, self.python_version = _engines.engine, _engines.python_version


class DocMachine(object):
    def __init__(self, lines):
        self.images = []
        title = []
        description = []
        pattern = re.compile("^\-([a-z_]{2,50})\-")
        current_lines = []
        for line in lines:
            m = pattern.match(line)
            if m:
                group = m.group(1)
                current_lines = []
                if group == 'title':
                    title = current_lines
                elif group == 'description':
                    description = current_lines
                elif group == 'images_url':
                    self.images = current_lines
            else:
                current_lines.append(line)
        self.title = '\n'.join(title)
        self.description = '\n'.join(description)


class InputsMachine(object):
    def __init__(self, lines):
        self.inputs = []
        patterns = ("^([a-z_]*)\(([a-zA-Z0-9_,.=\"\']*)\)",
                    "^([a-z_]*)\(([a-zA-Z0-9_,.=\"\']*) *, *\(([a-zA-Z0-9_,.:\"\']*)\)\)",
                    "^([a-z_]*)\(([a-zA-Z0-9_,.=\"\']*) *, *\[([a-zA-Z0-9_,.\"\']*)\]\)")
        pattern = re.compile("|".join(patterns))
        for line in lines:
            m = pattern.match(line)
            if m:
                var = None
                _range = []
                allowed_values = []
                name = None
                default = None
                if m.group(1):
                    _type = m.group(1)
                    var = m.group(2)
                elif m.group(3):
                    _type = m.group(3)
                    var = m.group(4)
                    values = m.group(5).split(':')
                    if len(values) <= 3 and len(values) >= 2:
                        for value in values:
                            _range = [value.strip() for value in values]
                elif m.group(6):
                    _type = m.group(6)
                    var = m.group(7)
                    allowed_values = [value.strip() for value in m.group(8).split(',')]

                var = var.split('=', 1)
                if len(var) == 2:
                    name, default = var
                else:
                    name = var[0]
                self.inputs.append([name, _type, default, _range, allowed_values])


class OutputsMachine(object):
    def __init__(self, lines):
        self.extensions = ['stl']
        pattern = re.compile("^\-([a-z_]{2,50})\-")
        current_lines = []
        for line in lines:
            m = pattern.match(line)
            if m:
                group = m.group(1)
                current_lines = []
                if group == 'extensions':
                    self.extensions = current_lines
            else:
                current_lines.append(line)


class DepsMachine(object):
    def __init__(self, lines):
        self.sysdeps = []
        self.pip = []
        pattern = re.compile("^\-([a-z_]{2,50})\-")
        current_lines = []
        for line in lines:
            m = pattern.match(line)
            if m:
                group = m.group(1)
                current_lines = []
                if group == 'system':
                    self.sysdeps = current_lines
                if group == 'pip':
                    self.pip = current_lines
            else:
                current_lines.append(line)


class EnginesMachine(object):
    def __init__(self, lines):
        self.engine = None
        self.python_version = None
        pattern = re.compile("^\-([a-z_]{2,50})\-")
        current_lines = []
        for line in lines:
            m = pattern.match(line)
            if m:
                group = m.group(1)
                current_lines = []
                if group == 'engine':
                    self.engine = current_lines
                if group == 'python':
                    self.python_version = current_lines
            else:
                current_lines.append(line)

        self.engine = self.engine[0] if self.engine else None
        self.python_version = self.python_version[0] if self.python_version else None

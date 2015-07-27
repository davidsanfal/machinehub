from machinehub.common.errors import MachinehubException, NotMachineHub
import uuid
import imp
import os
import inspect
import re
from machinehub.common.machinehub_logging import logger


def check_machine(machine_file):
    """ Check the integrity of a given machine
    """
    try:
        a = machine_file.__dict__['machinebuilder']
        if inspect.isfunction(a) and a.__doc__:
            machine_info = MachineParser(a.__doc__)
            return a, machine_info.doc, machine_info.inputs
        else:
            raise MachinehubException('machinebuilder must be a funcion with docstring')
    except KeyError as e:
        logger.info(e.message)
        raise NotMachineHub()


def load_machine(machine_path):
    """ loads a machine from the given file
    """
    # Check if precompiled exist, delete it
    if os.path.exists(machine_path + "c"):
        os.unlink(machine_path + "c")

    if not os.path.exists(machine_path):
        raise MachinehubException("%s not found!" % machine_path)

    # We have to generate a new name for each machine
    module_id = uuid.uuid1()
    try:
        loaded = imp.load_source("machine%s" % module_id, machine_path)
    except NotMachineHub:
        import traceback
        trace = traceback.format_exc().split('\n')
        raise MachinehubException("Unable to load machine in %s\n%s" % (machine_path,
                                                                        '\n'.join(trace[3:])))
    try:
        result = check_machine(loaded)
        return result
    except MachinehubException as e:  # re-raise with file name
        raise MachinehubException("%s: %s" % (machine_path, str(e)))


def load_machine_from_source(machine):
    """ loads a machine object from the given source
    """
    # We have to generate a new name for each machine
    module_id = uuid.uuid1()
    try:
        loaded = imp.new_module("machine%s" % module_id)
        exec machine in loaded.__dict__
    except KeyError as e:
        raise MachinehubException("Unable to load machine %s" % e.message)
    try:
        result = check_machine(loaded)
        return result
    except MachinehubException as e:  # re-raise with file name
        raise MachinehubException("machine: %s" % str(e))


class MachineParser(object):
    def __init__(self, text):
        self.doc = None
        self.inputs = None
        doc_lines = []
        inputs_lines = []
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
                else:
                    raise MachinehubException("MachineParser: Unrecognized field '%s'" % group)
            else:
                current_lines.append(line)
        self.doc = DocMachine(doc_lines)
        self.inputs = InputsMachine(inputs_lines).inputs


class DocMachine(object):
    def __init__(self, lines):
        self.images = []
        title = []
        description = []
        pattern = re.compile("^\-([a-z_]{2,50})\-")
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
                    raise MachinehubException("SectionParser: Unrecognized field '%s'" % group)
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
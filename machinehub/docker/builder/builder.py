import uuid
import imp
import os
import inspect
import sys
import json


class WorkerException(Exception):
    pass


class NotMachine(Exception):
    pass


def check_machine(machine_file):
    """ Check the integrity of a given machine
    """
    try:
        fn = machine_file.__dict__['machinebuilder']
        if inspect.isfunction(fn):
            return fn
        else:
            raise WorkerException('machinebuilder must be a funcion with docstring')
    except KeyError:
        raise NotMachine()


def load_machine(machine_path):
    """ loads a machine from the given file
    """
    # Check if precompiled exist, delete it
    if os.path.exists(machine_path + "c"):
        os.unlink(machine_path + "c")

    if not os.path.exists(machine_path):
        raise WorkerException("%s not found!" % machine_path)

    # We have to generate a new name for each machine
    module_id = uuid.uuid1()
    try:
        loaded = imp.load_source("machine%s" % module_id, machine_path)
    except NotMachine:
        import traceback
        trace = traceback.format_exc().split('\n')
        raise WorkerException("Unable to load machine in %s\n%s" % (machine_path,
                                                                    '\n'.join(trace[3:])))
    try:
        fn = check_machine(loaded)
        return fn
    except WorkerException as e:  # re-raise with file name
        raise WorkerException("%s: %s" % (machine_path, str(e)))


machine_id = sys.argv[1]
machine_name = sys.argv[2]

builder_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(builder_path)
machine_path = os.path.join(builder_path, 'machine', '%s.py' % machine_name)
fn = load_machine(machine_path)
with open(os.path.join(builder_path, 'machine', 'input%s.json' % machine_id)) as f:
    values = json.load(f)
    for val in values.keys():
        print val, values[val], type(values[val])
        if type(values[val]) == 'unicode':
            values[val] = str(values[val])
    real_file_path = os.path.join(builder_path,
                                  'machine',
                                  os.environ['OUTPUT_FOLDER'],
                                  values['file_path'])
    values['file_path'] = real_file_path
    os.chdir(os.path.join(builder_path, 'machine'))
    fn(**values)

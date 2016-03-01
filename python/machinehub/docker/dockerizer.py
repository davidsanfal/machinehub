
import os
from subprocess import Popen, PIPE
from jinja2 import Template
from machinehub.config import MACHINES_FOLDER, MACHINESOUT


Dockerfile_template = '''
FROM machinehub/{{ engine }}

ENV OUTPUT_FOLDER {{ output }}
RUN apt-get -y update
RUN apt-get -y upgrade

{% for sysdep in system_deps %}
RUN apt-get install -y {{ sysdep }}
{% endfor %}

{% for pydep in python_deps %}
RUN pip install {{ pydep }}
{% endfor %}
'''


def kill_and_remove(ctr_name):
    for action in ('kill', 'rm'):
        p = Popen('docker %s %s' % (action, ctr_name), shell=True,
                  stdout=PIPE, stderr=PIPE)
        if p.wait() != 0:
            raise RuntimeError(p.stderr.read())


def create_image(machine, system_deps, python_deps, engine):
    dockerfile_path = os.path.join(MACHINES_FOLDER, machine, 'Dockerfile')
    dockerfile = Template(Dockerfile_template)
    with open(dockerfile_path, 'w+') as f:
        f.write(dockerfile.render(output=MACHINESOUT,
                                  engine=engine,
                                  system_deps=system_deps,
                                  python_deps=python_deps))
    process = Popen(['docker', 'build', '-t', machine, '.'],
                    cwd=os.path.join(MACHINES_FOLDER, machine),
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    return stdout, stderr


def dockerize(machine, machine_id):
    machine_path = os.path.join(MACHINES_FOLDER, machine)
    container_name = '%s%s' % (machine.replace('/', '.'), machine_id)
    process = Popen(['docker', 'run', '--rm',
                     '-v', '%s:/worker/machine' % (machine_path),
                     '--name', container_name,
                     machine,
                     'python', 'builder.py', machine_id, machine.split('/')[1]],
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    print(stdout.decode('utf-8'))
    print('--------------------')
    print(stderr.decode('utf-8'))

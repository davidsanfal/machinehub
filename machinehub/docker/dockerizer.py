
import os
from subprocess import Popen, PIPE


path = os.path.dirname(os.path.realpath(__file__))


def kill_and_remove(ctr_name):
    for action in ('kill', 'rm'):
        p = Popen('docker %s %s' % (action, ctr_name), shell=True,
                  stdout=PIPE, stderr=PIPE)
        if p.wait() != 0:
            raise RuntimeError(p.stderr.read())


def execute(machine, options):
    p = Popen(['timeout', '-s', 'SIGKILL', '30',
               'docker', 'run', '--rm',
               ''
               'ubuntu:14.04', 'python3', '-c', code],
              stdout=PIPE)
    out = p.stdout.read()

    if p.wait() == -9:  # Happens on timeout
        # We have to kill the container since it still runs
        # detached from Popen and we need to remove it after because
        # --rm is not working on killed containers
        kill_and_remove(ctr_name)

    return out

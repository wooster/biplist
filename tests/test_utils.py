import os
import subprocess
import sys
import six

def data_path(path):
    return os.path.join(os.path.dirname(globals()["__file__"]), 'data', path)

def run_command(args, verbose = False):
    """Runs the command and returns the status and the output."""
    if verbose:
        sys.stderr.write("Running: %s\n" % command)
    p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdin, stdout = (p.stdin, p.stdout)
    output = stdout.read()
    output = output.strip(six.b("\n"))
    status = stdin.close()
    stdout.close()
    p.wait()
    return p.returncode, output

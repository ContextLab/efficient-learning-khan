# This script is run during build from Dockerfile-analyses.
# It deals with installing conda, pip, and local packages,
# as well as downloading some data and configuring some jupyter
# extensions needed to run the analysis notebooks
import sys
import time
from shlex import split as split_command
from subprocess import PIPE, Popen, CalledProcessError, TimeoutExpired


def run_with_live_output(command, timeout=None, **popen_kwargs):
    """
    Runs a shell command via subprocess.Popen and captures
    stdout in real-time.
    """
    cmd = split_command(command)
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, **popen_kwargs)
    if timeout is not None:
        start_time = time.time()

    # poll method returns None until process terminates
    while True:
        retcode = process.poll()
        if retcode is None:
            output = process.stdout.readline().strip().decode()
            if output:
                print(output)
            if (timeout is not None) and (time.time() - start_time > timeout):
                # clean up child process
                process.kill()
                raise TimeoutExpired(cmd=command, timeout=timeout)

        elif retcode != 0:
            # process returned non-zero exit status
            raise CalledProcessError(returncode=retcode, cmd=command)
        else:
            return process


commands = [
    # update setuptools
    "conda update -y setuptools",
    # install jupyterlab
    "conda install -yc conda-forge jupyterlab",
    # install proper package versions (use pip to avoid
    # dreadfully slow conda compatibility checks)
    "pip install -r analyses-requirements.txt",
    # install helper module as a package for easier importing in notebooks
    "pip install /buildfiles/khan_helpers",
    # install js & css files for some convenient jupyter notebook extensions
    "jupyter contrib nbextension install --user",
    # download various nltk packages
    # (has to be run in a subprocess because nltk wasn't installed when this interpreter was loaded)
    # (Warnings filter ignores harmless RuntimeWarning https://github.com/nltk/nltk/issues/2162)
    "python -W ignore -m nltk.downloader stopwords averaged_perceptron_tagger wordnet"
]

for i, command in enumerate(commands):
    print(f'\n\nRunning step {i + 1}/{len(commands)}: "{command}"')
    run_with_live_output(command, timeout=120)

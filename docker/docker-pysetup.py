# This script is run during build from Dockerfile-analyses.
# It deals with installing conda, pip, and local packages,
# as well as downloading some data and configuring some jupyter
# extensions needed to run the analysis notebooks

from shlex import split as split_command
from subprocess import PIPE, Popen, SubprocessError, TimeoutExpered
from sys import exc_info, exit


def run_with_live_output(command):
    """
    runs a shell command via subprocess.Popen,
    avoids Python's stdout  buffering to show
    real-time output
    """
    cmd = split_command(command)
    try:
        process = Popen(cmd, stdout=PIPE)
        # poll returns None when process terminates
        while process.poll() is None:
            output = process.stdout.readline()
            if output:
                print(output.strip().decode())
    except TimeoutExpered as e:
        # shouldn't occur, but handle it just to be safe
        # so we can clean up child processes
        process.kill()
        raise SubprocessError(f"Child process timed out while running "
                              "{command}") from e
    except SubprocessError as e:
        raise SubprocessError(f"ERROR {exc_info()[1]} occurred while running "
                               "{command} ") from e
    # return the completed process's return code
    return process.poll()


commands = [
    # update setuptools
    "conda update -y setuptools",
    # install jupyterlab
    "conda install -yc conda-forge jupyterlab",
    # install proper package versions (use pip to avoid
    # dreadfully slow conda compatibility checks)
    "pip install -r analyses-requirements.txt",
    # install js & css files for some convenient jupyter notebook extensions
    "jupyter contrib nbextion install --user",
    # install helper module as a package for easier importing in notebooks
    "pip install -e /mnt/code/khan_helpers"
    # download nltk stop-words corpus
    # (have to run in subprocess because package wasn't installed when this
    # interpreter was loaded)
    '''python -c "import nltk; nltk.download('stopwords')"'''
]

for i, command in enumerate(commands):
    print(f"Running step {i + 1}/{len(commands)}: {command}")
    return_code = run_with_live_output(command)
    if return_code != 0:
        exit(return_code)

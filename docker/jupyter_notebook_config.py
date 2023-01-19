"""
Config file for the Jupyter notebook server.

Sets some options for serving notebooks from inside a Docker container
based on arguments passed during build.
"""
from os import getenv


c.Completer.use_jedi = False
c.IPCompleter.use_jedi = False
c.NotebookApp.ip = getenv("NOTEBOOK_IP")
c.NotebookApp.port = int(getenv("NOTEBOOK_PORT"))
c.NotebookApp.notebook_dir = getenv("NOTEBOOK_DIR")
c.NotebookApp.open_browser = False
c.NotebookApp.allow_root = True
# https://github.com/jupyter/notebook/issues/3130
c.NotebookApp.delete_to_trash = False

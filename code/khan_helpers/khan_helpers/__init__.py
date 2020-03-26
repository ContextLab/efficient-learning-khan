from os.path import dirname, realpath
from pkg_resources import get_distribution
from IPython.display import display, Markdown

from .experiment import Experiment
from .participant import Participant


# see version number in setup.py
__version__ = get_distribution("khan_helpers").version

github_link = "https://github.com/contextlab/efficient-learning-khan/tree/master/code/khan_helpers"
pkg_dir = dirname(dirname(realpath(__file__)))
message = Markdown(
    "Experiment & Paricipant classes, helper functions, and variables used "
    f"across multiple notebooks can be found in `{pkg_dir}`, or on GitHub, "
    f"[here]({github_link}).<br />You can also view source code directly from "
    "the notebook with:<br /><pre>    from khan_helpers.helpers import "
    "show_source<br />    show_source(foo)</pre>"
)

try:
    # check whether imported from notebook
    get_ipython()
    display(message)
except NameError:
    pass

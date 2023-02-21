from pathlib import Path

from IPython.display import display, Markdown

from .experiment import Experiment
from .participant import Participant
from .functions import set_figure_style


version_info = (0, 0, 1)
__version__ = '.'.join(map(str, version_info))

github_link = "https://github.com/contextlab/efficient-learning-khan/tree/master/code/khan_helpers"
pkg_dir = Path(__file__).resolve().parent
message = Markdown(
    "Experiment & Participant classes, helper functions, and variables used "
    f"across multiple notebooks can be found in `{pkg_dir}`, or on GitHub, "
    f"[here]({github_link}).<br />You can also view source code directly from "
    "the notebook with:<br /><pre>    from khan_helpers.functions import "
    "show_source<br />    show_source(foo)</pre>"
)

try:
    # check whether imported from notebook
    # noinspection PyUnresolvedReferences
    #   function is defined globally by IPython
    get_ipython()
    display(message)
except NameError:
    pass

set_figure_style()

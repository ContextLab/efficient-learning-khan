from pkg_resources import get_distribution
from IPython.display import display, Markdown


# see version number in setup.py
__version__ = get_distribution("khan_helpers").version

github_link = "https://github.com/contextlab/efficient-learning-khan/tree/master/code/khan_helpers"
message = Markdown(
    "Experiment & Paricipant classes, helper functions, and variables used "
    f"across multiple notebooks may be found [here]({github_link}).<br />"
    "You can also view source code directly from the notebook with:<br />"
    "<pre>    from khan_helpers.helpers import show_source<br />    "
    "show_source(foo)</pre>"
)

try:
    # check for InteractiveShell method
    get_ipython()
    display(message)
except NameError:
    pass

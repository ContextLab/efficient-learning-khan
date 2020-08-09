import re
from collections import defaultdict
from datetime import timedelta
from difflib import get_close_matches
from inspect import getsource
from typing import Iterator

import numpy as np
import pandas as pd
from IPython.display import display, HTML
from IPython.core.oinspect import pylight
from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from scipy.interpolate import interp1d
from scipy.spatial.distance import cdist

from .constants import LECTURE_WSIZE, STOP_WORDS


########################################
#          TEXT PREPROCESSING          #
########################################

def _ts_to_sec(ts):
    # converts timestamp of elapsed time from "MM:SS" format to scalar
    mins, secs = ts.split(':')
    return timedelta(minutes=int(mins), seconds=int(secs)).total_seconds()


def parse_windows(transcript, wsize=LECTURE_WSIZE):
    """
    Formats lecture transcripts as overlapping sliding windows to feed
    as documents to topic model.  Also assigns a timestamp to each
    window used for interpolating the topic trajectory.

    Parameters
    ----------
    transcript : str
        The lecture transcript as a single string, with alternating,
        `\n`-separated lines of timestamps and transcribed speech.
    wsize : int, optional
        The number of text lines comprising each sliding window (with
        tapering window sizes at the beginning and end).  Defaults to
        the window size chosen by the parameter optimization.

    Returns
    -------
    windows : list of str
        The overlapping sliding windows.
    timestamps : list of int
        The timestamps corresponding to each window.

    """
    lines = transcript.splitlines()
    text_lines = lines[1::2]
    ts_lines = list(map(_ts_to_sec, lines[::2]))
    windows = []
    timestamps = []
    for ix in range(1, wsize):
        start, end = 0, ix
        windows.append(' '.join(text_lines[start:end]))
        timestamps.append((ts_lines[start] + ts_lines[end - 1]) / 2)

    for ix in range(len(ts_lines)):
        start = ix
        end = ix + wsize if ix + wsize <= len(text_lines) else len(text_lines)
        windows.append(' '.join(text_lines[start:end]))
        timestamps.append((ts_lines[start] + ts_lines[end - 1]) / 2)

    return windows, timestamps


def preprocess_text(textlist, man_changes=None):
    """
    Handles text preprocessing of lecture transcripts and quiz questions
    & answers.  Performs case and whitespace normalization, punctuation
    and non-alphabetic character removal, stop word removal,
    POS tagging, and lemmatization.

    Occasionally, the Treebank POS tagger mis-tags a word, which causes
    WordNet's "Morphy" to apply the morphologocal transformations and
    detachment rules for the wrong syntactic category, and fail to
    lemmatize the word.  The function attempts to handle these
    instances and can optionally record corrections made this way for
    visual inspection to ensure no improper substitutions were made.

    Parameters
    ----------
    textlist : list of str
        List of text samples (lecture transcript lines, quiz questions,
        or quiz answers) to be processed.
    man_changes : collections.defaultdict, optional
        A `collections.defaultdict` instance with `default_factory=int`,
        used for recording instances where lemmatization was performed
        manually. If provided, keys of (word, lemma) will be added or
        incremented for each manual replacement.

    Returns
    -------
    processed_textlist : list of str
        The original `textlist` with preprocessing steps applied to each
        element.

    """
    if man_changes is not None:
        assert isinstance(man_changes, defaultdict)

    # define some constants only used in this function:
    lemmatizer = WordNetLemmatizer()
    # suffixes to detect for manual lemmatization
    man_lemmatize_sfxs = ('s', 'ing', 'ly', 'ed', 'er', 'est')
    # mapping between Treebank and WordNet POS tags
    tagset_mapping = defaultdict(lambda: 'n')
    for tb_tag, wn_tag in zip(['N', 'P', 'V', 'J', 'D', 'R'],
                              ['n', 'n', 'v', 'a', 'a', 'r']):
        tagset_mapping[tb_tag] = wn_tag

    # indices to map processed words back to correct textlist item
    chunk_ix = [ix for ix, chunk in enumerate(textlist) for _ in chunk.split()]
    processed_chunks = [[] for i in textlist]
    # clean spacing, normalize case, strip puncutation
    # (temporarily leave punctuation useful for POS tagging)
    full_text = ' '.join(textlist).lower()
    punc_stripped = re.sub("[^a-zA-Z\s'-]+", '', full_text)
    # POS tagging (works better on full transcript, more context provided)
    words_tags = pos_tag(punc_stripped.split())

    for i, (word, tag) in enumerate(words_tags):
        # discard contraction clitics (always stop words) post-tagging
        # irregular stems (don, isn, etc.) handled by stop word removal
        if "'" in word:
            word = word.split("'")[0]

        # remove stop words & digits
        if word in STOP_WORDS or word[0].isdigit():
            continue

        # convert Treebank POS tags to WordNet POS tags
        tag = tagset_mapping[tag[0]]
        # lemmatize
        lemma = lemmatizer.lemmatize(word, tag)

        # handles most cases where POS tagger misidentifies a word, causing
        # WordNet Morphy to use the wrong syntactic transformation and fail
        if (
                lemma == word
                and any(word.endswith(sfx) for sfx in man_lemmatize_sfxs)
                and len(word) > 4
        ):
            lemma = synset_match(word)
            if lemma != word and man_changes is not None:
                # record changes made this way to spot-check later
                man_changes[(word, lemma)] += 1

        # split on hyphens, place back in correct text chunk
        processed_chunks[chunk_ix[i]].append(lemma.replace('-', ' '))

    # join words within each chunk
    return [' '.join(c) for c in processed_chunks]


def synset_match(word, min_similarity=0.6):
    """
    Attempts to manually identify the proper lemma for a given `word`.
    Searches WordNet's database of cognitive synonyms for the provided
    `word` (its "synset") as well as the pertainyms of each word in the
    synset (to handle adverb-adjective relationships).

    Works based on the assumption that the correct lemma is the most
    similar choice (via `difflib.SequenceMatcher`) to the original word
    *that is also shorter than the original word*.

    Parameters
    ----------
    word : str
        The word to be lemmatized.
    min_similarity : float, optional
        The minimum similarity to the provided word for a possible lemma
        to be considered correct (default: 0.6).

    Returns
    -------
    lemma : str
        If a lemma for the provided word was identified, it is returned.
        Otherwise, the original word is returned.

    """
    possible_matches = []
    for synset in wordnet.synsets(word):
        for lemma in synset.lemmas():
            possible_matches.append(lemma.name())
            for pert in lemma.pertainyms():
                possible_matches.append(pert.name())

    possible_matches = list(set(possible_matches))
    possible_matches = [m.lower() for m in possible_matches if len(m) <= len(word)]
    # sort by similarity to word
    close_matches = get_close_matches(word, possible_matches, n=2, cutoff=min_similarity)
    if len(close_matches) == 0:
        return word
    # if original word was in synset lemmas and the second closest possibility is shorter, use that
    elif (close_matches[0] == word) and (len(close_matches) > 1) and (len(close_matches[1]) < len(word)):
        return close_matches[1]
    else:
        return close_matches[0]


########################################
#        STATS/MATH FUNCTIONS          #
########################################

def corr_mean(rs, axis=None, **kwargs):
    """
    Computes the mean of a set of correlation coefficients, performing
    the Fisher *z*-transformation before averaging and the inverse
    transformation on the result.

    Parameters
    ----------
    rs : array_like
        Array of *r*-values.  May be any type accepted by `numpy.mean`
    axis : None or int or tuple of ints, optional
        Axis or axes along which the means are computed. If None
        (default), the mean of the flattened array is computed.
    kwargs : various types, optional
        Additional keyword arguments passed to `numpy.mean` (see
        https://numpy.org/doc/stable/reference/generated/numpy.mean.html)

    Returns
    -------
    cm : float or numpy.ndarray
        The average correlation coefficient

    """
    return z2r(np.nanmean([r2z(r) for r in rs], axis=axis, **kwargs))


def interp_lecture(lec_traj, timestamps):
    """
    Interpolates a lecture's topic trajectory to a resolution of 1
    vector per second.

    Parameters
    ----------
    lec_traj : numpy.ndarray
        A (timepoints, topics) array with a topic vector for each
        sliding window.
    timestamps : array_like
        A 1-D array of timestamps for each sliding window.

    Returns
    -------
    traj_interp : numpy.ndarray
        A (timepoints, topics) array with a topic vector for each second.

    """
    new_tpts = np.arange(timestamps[-1])
    interp_func = interp1d(timestamps, lec_traj, axis=0)
    return interp_func(new_tpts)


def rbf_sum(obs_coords, pred_coords, width, metric='euclidean'):
    """
    Given a set of observed coordinates and predicted coordinates,
    computes the (unweighted) sum of Gaussian radial basis functions
    centered on each observed coordinate, evaluated at each predicted
    coordinate.

    Parameters
    ----------
    obs_coords : numpy.ndarray
        An (x, z) array of coordinates for *x* nodes in *z* dimensions.
    pred_coords : numpy.ndarray
        A (y, z) array of coordinates for *y* points in *z* dimensions
        at which to evaluate the RBFs.
    width : scalar
        The Width of the Gaussian kernel.
    metric : str or callable, optional
        The metric used for measuring distance between two points.  May
        be any metric accepted by `scipy.spatial.distance.cdist`.

    Returns
    -------
    rbf_sums : numpy.ndarray
        A (y,) array of summed RBFs evaluated at each

    """
    dmat = cdist(obs_coords, pred_coords, metric=metric)
    return np.exp(-dmat ** 2 / width).sum(axis=0)


def r2z(r):
    """
    Computes the Fisher *z*-transformation.

    Parameters
    ----------
    r : scalar or numpy.ndarray
        Correlation value(s).

    Returns
    -------
    z : *z*-transformed correlation value(s).

    """
    with np.errstate(invalid='ignore', divide='ignore'):
        return 0.5 * (np.log(1 + r) - np.log(1 - r))


def z2r(z):
    """
    Computes the inverse Fisher *z*-transformation.

    Parameters
    ----------
    z : scalar or numpy.ndarray
        *z*-transformed correlation value(s).

    Returns
    -------
    r : scalar or numpy.ndarray
        Correlation value(s).

    """
    # computes the inverse Fisher z-transformation
    with np.errstate(invalid='ignore', divide='ignore'):
        return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)


########################################
#          NOTEBOOK DISPLAYS           #
########################################

def multicol_display(*outputs,
                     ncols=2,
                     caption=None,
                     col_headers=None,
                     table_css=None,
                     caption_css=None,
                     header_css=None,
                     row_css=None,
                     cell_css=None):
    """
    Renders notebook cell output in multiple side-by-side columns using
    an HTML table.  Accepts a variable number of output items and
    "wraps" the columns into multiple rows if `len(outputs) > ncols`

    Parameters
    ----------
    outputs : Objects
        Objects to be placed in each table cell, passed as positional
        arguments.  May be any Python class that defines a `__str__`
        and/or `__repr__` method.
    ncols : int, optional
        The number of columns for the display (default: 2).  If less
        than the number of outputs passed, the display will include
        multiple rows.
    caption : str, optional
        Text passed to the table's `<caption>` tag, displayed above the
        table.
    col_headers : list-like of str, optional
        Contents of table header (`<th>`) elements for each column.  If
        passed, must have length equal `ncols`.  If `None` (default),
        table header elements are not created.
    table_css : dict, optional
        Additional CSS properties to be applied to the outermost
        (`<table>`) element.
    caption_css : dict, optional
        Additional CSS properties to be applied to the table *caption*
        (`<caption>`) element.
    header_css : dict, optional
        Additional CSS properties to be applied to each table *header*
        (`<th>`) element.
    row_css : dict, optional
        Additional CSS properties to be applied to each table *row*
        (`<tr>`) element.
    cell_css : dict, optional
        Additional CSS properties to be applied to each table *cell*
        (`<td>`) element.

    Returns
    -------
    None
        The HTML table is displayed inline in the notebook.

    """
    def _fmt_python_types(obj):
        # formats some common Python objects for display
        if isinstance(obj, str):
            return obj.replace('\n', '<br>')
        elif isinstance(obj, (int, float)):
            return str(obj)
        elif (isinstance(obj, (list, tuple, set, Iterator))
              or type(obj).__module__ == 'numpy'):
            return ', '.join(obj)
        elif isinstance(obj, dict):
            return '<br><br>'.join(f'<b>{k}</b>:&emsp;{_fmt_python_types(v)}'
                                   for k, v in obj.items())
        elif isinstance(obj, pd.DataFrame):
            return obj.to_html()
        else:
            return obj

    if col_headers is None:
        col_headers = []
    else:
        assert hasattr(col_headers, '__iter__') and len(col_headers) == ncols

    outs_fmt = []
    for out in outputs:
        outs_fmt.append(_fmt_python_types(out))

    table_css = {} if table_css is None else table_css
    caption_css = {} if caption_css is None else caption_css
    header_css = {} if header_css is None else header_css
    row_css = {} if row_css is None else row_css
    cell_css = {} if cell_css is None else cell_css

    # set some reasonable default style properties
    table_css_defaults = {
        'width': '100%',
        'border': '0px',
        'margin-left': 'auto',
        'margin-right': 'auto'
    }
    caption_css_defaults = {
        'color': 'unset',
        'text-align': 'center',
        'font-size': '2em',
        'font-weight': 'bold'
    }
    header_css_defaults = {
        'border': '0px',
        'font-size': '16px',
        'text-align': 'center'
    }
    row_css_defaults = {'border': '0px'}
    cell_css_defaults = {
        'border': '0px',
        'width': f'{100 / ncols}%',
        'vertical-align': 'top',
        'font-size': '14px',
        'text-align': 'center'
    }

    # update/overwrite style defaults with passed properties
    table_css = dict(table_css_defaults, **table_css)
    caption_css = dict(caption_css_defaults, **caption_css)
    header_css = dict(header_css_defaults, **header_css)
    row_css = dict(row_css_defaults, **row_css)
    cell_css = dict(cell_css_defaults, **cell_css)

    # format for string replacement in style tag
    table_style = ";".join(f"{prop}:{val}" for prop, val in table_css.items())
    caption_style = ";".join(f"{prop}:{val}" for prop, val in caption_css.items())
    header_style = ";".join(f"{prop}:{val}" for prop, val in header_css.items())
    row_style = ";".join(f"{prop}:{val}" for prop, val in row_css.items())
    cell_style = ";".join(f"{prop}:{val}" for prop, val in cell_css.items())

    # string templates for individual elements
    html_table = f"<table style={table_style}>{{caption}}{{header}}{{content}}</table>"
    html_caption = f"<caption style={caption_style}>{{content}}</caption>"
    html_header = f"<th style={header_style}>{{content}}</th>"
    html_row = f"<tr style={row_style}>{{content}}</tr>"
    html_cell = f"<td style={cell_style}>{{content}}</td>"

    # fill element templates with content
    cap = html_caption.format(content=caption) if caption is not None else ''
    headers = [html_header.format(content=h) for h in col_headers]
    cells = [html_cell.format(content=out) for out in outs_fmt]
    rows = [html_row.format(content="".join(cells[i:i+ncols])) for i in range(0, len(cells), ncols)]
    # render notebook display cell
    display(HTML(html_table.format(caption=cap,
                                   header="".join(headers),
                                   content="".join(rows))))


def show_source(obj):
    """
    Displays the source code for an object defined outside the current notebook.

    Parameters
    ----------
    obj : Object
        The object to display.  If `obj` is a module, class, method,
        function, traceback, frame, or other code object, its source
        code will be displayed inline with syntax highlighting.
        Otherwise, a string representation of the object will be
        displayed, if available.

    Returns
    -------
    None
        The source code or object is displayed inline in the notebook.

    """
    try:
        src = getsource(obj)
    except TypeError as e:
        # if called on variable, just show its value
        src = obj
    try:
        return HTML(pylight(src))
    except AttributeError:
        # pylight just doesn't work on certain types
        return src

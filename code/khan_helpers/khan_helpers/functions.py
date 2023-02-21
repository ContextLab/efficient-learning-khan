import logging
import math
import re
import warnings
from collections import defaultdict
from contextlib import contextmanager, nullcontext
from datetime import timedelta
from difflib import get_close_matches
from inspect import getsource
from typing import Iterator

import matplotlib.pyplot as plt
import numba
import numpy as np
import pandas as pd
from IPython.display import display, HTML
from IPython.core.oinspect import pylight
from matplotlib import font_manager
from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from scipy.interpolate import interp1d
from scipy.spatial.distance import cdist

from .constants import FONTS_DIR, LECTURE_WSIZE, STOP_WORDS


def _ts_to_sec(ts):
    """
    Converts a timestamp denoting elapsed time from "MM:SS[.ss]" format
    to a scalar

    Parameters
    ----------
    ts : str
        A timestamp consisting of minutes and seconds, separated by a
        colon, where seconds may be a whole number or a decimal.

    Returns
    -------
    float
        The total number of seconds represented by the timestamp.
    """
    mins, secs = ts.split(':')
    return timedelta(minutes=int(mins), seconds=float(secs)).total_seconds()


def bootstrap_ci_plot(
        M,
        ci=95,
        n_boots=1000,
        ignore_nan=False,
        color=None,
        alpha=0.3,
        return_bounds=False,
        label=None,
        ax=None,
        line_kwargs=None,
        ribbon_kwargs=None
):
    """
    Plots a timeseries of observations with error ribbons denoting the
    bootstrap-estimated confidence interval at each timepoint. Looks
    very similar to `seaborn.lineplot`, but runs about 2-3 times faster.

    Parameters
    ----------
    M : numpy.ndarray
        A (timepoints, observations) array of values for plotting
    ci : int, optional
        The size of the confidence interval as a percentage (default:
        95).
    n_boots : int, optional
        The number of bootstraps to use for computing the confidence
        interval (default: 1,000). Full-size resamples of observations
        are constructed (with replacement) independently for each
        timepoint.
    ignore_nan : bool, optional
        If True (default: False), ignore NaNs in all calculations
        (handle them with numpy NaN-aware functions and suppress common
        NaN-related warnings).
    color : str or tuple of float, optional
        Any color specification accepted by Matplotlib. See
        https://matplotlib.org/3.5.1/tutorials/colors/colors.html for a
        full list of options. Unless otherwise specified in
        `ribbon_kwargs`, this also sets the color of the CI ribbon.
        Defaults to the first color in the currently set palette.
    alpha : float, optional
        Alpha value for the CI ribbon (default: 0.3).
    return_bounds : bool, optional
        If True (default: False), return arrays containing the lower and
        upper bounds of the computed confidence interval for each
        timepoint in addition to the axis object.
    label : str, optional
        Label assigned to the line if constructing a legend.
    ax : matplotlib.axes.Axes, optional
        The axes on which to draw the plot. Defaults to the current Axes
        object (via `plt.gca()`).
    line_kwargs : dict, optional
        Additional keyword arguments forwarded to
        `matplotlib.axes.Axes.plot`.
    ribbon_kwargs : dict, optional
        Additional keyword arguments forwarded to
        `matplotlib.axes.Axes.fill_between`.

    Returns
    -------
    returns : matplotlib.axes.Axes or tuple of objects
        Return value depends on the value passed to `return_bounds`. If
        False (default), the Axes object alone is returned. If True, a
        3-tuple is returned, where the first item is the Axes object and
        the second and third items are 1-D Numpy arrays respectively
        containing the lower and upper bounds of the confidence interval
        at each timepoint.
    """
    # set defaults
    if ignore_nan:
        nan_context = filter_nan_warnings
        mean_func = np.nanmean
        percentile_func = np.nanpercentile
    else:
        nan_context = nullcontext
        mean_func = np.mean
        percentile_func = np.percentile
    if ax is None:
        ax = plt.gca()
    if line_kwargs is None:
        line_kwargs = {}
    if ribbon_kwargs is None:
        ribbon_kwargs = {}
    if color is None:
        color = plt.rcParams['axes.prop_cycle'].by_key()['color'][0]
    if 'color' not in ribbon_kwargs:
        ribbon_kwargs['color'] = color

    timepoints = np.arange(M.shape[0])
    with nan_context():
        obs_mean = mean_func(M, axis=1)

    # (n_tpts, n_obs, n_boots) column indices to subsample each row of M
    rand_ixs = np.random.randint(0, M.shape[1], size=(*M.shape, n_boots))
    # (n_tpts, n_boots) subsample means for each timepoint
    boots = np.take_along_axis(M[:, None], rand_ixs, axis=2)
    with nan_context():
        boot_means = mean_func(boots, axis=1)

        ci_low = percentile_func(boot_means, (100 - ci) / 2, axis=1)
        ci_high = percentile_func(boot_means, (100 + ci) / 2, axis=1)

    ax.fill_between(timepoints, ci_low, ci_high, alpha=alpha, **ribbon_kwargs)
    ax.plot(timepoints, obs_mean, color=color, label=label, **line_kwargs)

    if return_bounds:
        return ax, ci_low, ci_high
    return ax


def corr_mean(rs, axis=None, fix_inf=False, **kwargs):
    """
    Computes the mean of a set of correlation coefficients, performing
    the Fisher *z*-transformation before averaging and the inverse
    transformation on the result.

    Parameters
    ----------
    rs : array_like
        Array of *r*-values.  May be any type accepted by
        `numpy.nanmean()`.
    axis : None or int or tuple of ints, optional
        Axis or axes along which the means are computed. If `None`
        (default), the mean of the flattened array is computed.
    fix_inf : bool, optional
        See `z2r()` docstring for details. Default: False.
    **kwargs : various types, optional
        Additional keyword arguments passed to `numpy.nanmean` (see
        https://numpy.org/doc/stable/reference/generated/numpy.nanmean.html
        for details).

    Returns
    -------
    float or numpy.ndarray
        The mean correlation coefficient

    """
    zs = r2z(np.asanyarray(rs), fix_inf=fix_inf)
    zmean = np.nanmean(zs, axis=axis, **kwargs)
    return z2r(zmean)


@numba.njit
def correlation_exp(x, y):
    """
    Computes the correlation distance between two n-dimensional
    vectors, exponentiating each element first. Returns the result and
    the gradient of the distance function with respect to `x`.

    Parameters
    ----------
    x, y : numpy.ndarray
        The two vectors to compare. Must have the same shape.

    Returns
    -------
    dist : float
        Correlation distance between the two vectors.
    grad : numpy.ndarray
        Gradient of the distance with respect to `x`.
    """
    x = math.e ** x
    y = math.e ** y
    mu_x = 0.0
    mu_y = 0.0
    norm_x = 0.0
    norm_y = 0.0
    dot_product = 0.0

    for i in range(x.shape[0]):
        mu_x += x[i]
        mu_y += y[i]

    mu_x /= x.shape[0]
    mu_y /= x.shape[0]

    for i in range(x.shape[0]):
        shifted_x = x[i] - mu_x
        shifted_y = y[i] - mu_y
        norm_x += shifted_x ** 2
        norm_y += shifted_y ** 2
        dot_product += shifted_x * shifted_y

    if norm_x == 0.0 and norm_y == 0.0:
        dist = 0.0
        grad = np.zeros(x.shape)
    elif dot_product == 0.0:
        dist = 1.0
        grad = np.zeros(x.shape)
    else:
        dist = 1.0 - (dot_product / np.sqrt(norm_x * norm_y))
        grad = ((x - mu_x) / norm_x - (y - mu_y) / dot_product) * dist

    return dist, grad


@contextmanager
def disable_logging(module, level='CRITICAL'):
    """
    Temporarily disables logging from `module` for messages less severe
    than `level`.

    Parameters
    ----------
    module : str
        The qualified name of the module for which to disable logging.
    level : str, optional
        The threshold of messages below which to disable logging
        (default: 'CRITICAL'). Note that messages *of* the specified
        level will still be logged.
    """
    if module not in logging.root.manager.loggerDict:
        raise ValueError(f"no logger exists for module '{module}'")

    logger = logging.getLogger(module)
    old_level = logger.level
    logger.setLevel(level.upper())
    try:
        yield
    finally:
        logger.setLevel(old_level)


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
    "wraps" the columns into multiple rows if 'len(outputs) > ncols'

    Parameters
    ----------
    outputs : Objects
        Objects to be placed in each table cell, passed as positional
        arguments.  May be any Python class that defines a '__str__'
        and/or '__repr__' method.
    ncols : int, optional
        The number of columns for the display (default: 2).  If less
        than the number of outputs passed, the display will include
        multiple rows.
    caption : str, optional
        Text passed to the table's '<caption>' tag, displayed above the
        table.
    col_headers : list-like of str, optional
        Contents of table header ('<th>') elements for each column.  If
        passed, must have length equal 'ncols'.  If 'None' (default),
        table header elements are not created.
    table_css : dict, optional
        Additional CSS properties to be applied to the outermost
        ('<table>') element.
    caption_css : dict, optional
        Additional CSS properties to be applied to the table *caption*
        ('<caption>') element.
    header_css : dict, optional
        Additional CSS properties to be applied to each table *header*
        ('<th>') element.
    row_css : dict, optional
        Additional CSS properties to be applied to each table *row*
        ('<tr>') element.
    cell_css : dict, optional
        Additional CSS properties to be applied to each table *cell*
        ('<td>') element.
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
    rows = [html_row.format(content="".join(cells[i:i+ncols]))
            for i in range(0, len(cells), ncols)]
    # render notebook display cell
    display(HTML(html_table.format(caption=cap,
                                   header="".join(headers),
                                   content="".join(rows))))


@contextmanager
def filter_nan_warnings():
    """Temporarily filter warnings about NaN values in arrays."""
    message = 'Mean of empty slice|All-NaN slice encountered'
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore',
                                message=message,
                                category=RuntimeWarning)
        yield


def format_stats(stat, p, stat_name, df=None, n_decimals=3, p_min=0.001):
    """
    General function to format the test statistic and p-value from a
    statistical test for display in a `matplotlib.pyplot` plot.

    Parameters
    ----------
    stat, p : float
        The test statistic and associated p-value.
    stat_name : str
        The string used to describe the test statistic in the plot
        (e.g., 't', 'r', etc.).
    df : int, optional
        The degrees of freedom associated with the test statistic. If
        not None (default), this is displayed in parentheses immediately
        after the test statistic (e.g., "t(10) = ...").
    n_decimals : int, optional
        The number of decimals (default: 3) to display for the test
        statistic and p-value (if greater than `p_min`).
    p_min : float, optional
        The smallest p-value (default: 0.001) to display. Lower p-values
        are displayed as "p < `p_min`".

    Returns
    -------
    str
        The formatted output to display in the plot.
    """
    stat_fmt = f'$\\mathit{{{stat_name}}}\mathbf{{'
    if df is not None:
        stat_fmt = f'{stat_fmt}({df})'

    stat_fmt = f'{stat_fmt} = {stat:.{n_decimals}f}}}$\n$\\mathit{{p}}\mathbf{{'
    if p < p_min:
        p_fmt = ' < 0.001'
    else:
        p_fmt = f' = {p:.{n_decimals}f}'

    return f'{stat_fmt}{p_fmt}}}$'


def get_top_words(cv, lda, n_words=10):
    """
    Returns the top-weighted `n_words` words from each topic learned by
    a fit Latent Dirichlet Allocation model.

    Parameters
    ----------
    cv : sklearn.feature_extraction.text.CountVectorizer
        Fit Count Vectorizer model used to tokenize the corpus.
    lda : sklearn.decomposition.LatentDirichletAllocation
        Fit Latent Dirichlet Allocation model.
    n_words : int, optional
        Number of top-weighted words to return for each topic (default:
        10).

    Returns
    -------
    topic_words : {int: list of str}
        Dictionary of top-weighted words for each topic. Keys are topic
        indices; values are lists of `n_words` top words, in order.
    """
    topic_words = {}
    vocab = cv.get_feature_names_out()
    for topic, component in enumerate(lda.components_):
        word_ix = np.argsort(component)[::-1][:n_words]
        topic_words[topic] = [vocab[i] for i in word_ix]
    return topic_words


def interp_lecture(lec_traj, timestamps):
    """
    Interpolate an irregular timeseries of feature vectors to a
    resolution of 1 sample per second.

    Parameters
    ----------
    lec_traj : array_like
        A (timepoints, features) array with a feature vector for each
        sliding window.
    timestamps : array_like
        A 1-D array of timestamps for each sliding window.

    Returns
    -------
    numpy.ndarray
        A (timepoints, features) array with a feature vector for each
        second.
    """
    new_tpts = np.arange(timestamps[-1])
    interp_func = interp1d(timestamps,
                           lec_traj,
                           axis=0,
                           fill_value='extrapolate')
    return interp_func(new_tpts)


def parse_windows(transcript, wsize=LECTURE_WSIZE):
    """
    Formats lecture transcripts as overlapping sliding windows to feed
    as documents to topic model.  Also assigns a timestamp to each
    window used for interpolating the topic trajectory.

    Parameters
    ----------
    transcript : str
        The lecture transcript as a single string, with alternating,
        '\n'-separated lines of timestamps and transcribed speech.
    wsize : int, optional
        The number of text lines comprising each sliding window (with
        tapering window sizes at the beginning and end).  Defaults to
        `khan_helpers.constants.LECTURE_WSIZE`.

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
    # linearly shift all timestamps so the first one is 0s
    ts_lines = [ts - ts_lines[0] for ts in ts_lines]

    windows = []
    timestamps = []
    for ix in range(1, wsize):
        start, end = 0, ix
        windows.append(' '.join(text_lines[start:end]))
        # each window assigned to midpoint between timestamp of first
        # line and last lines
        timestamps.append((ts_lines[start] + ts_lines[end - 1]) / 2)

    for ix in range(len(ts_lines)):
        start = ix
        end = ix + wsize if ix + wsize <= len(text_lines) else len(text_lines)
        windows.append(' '.join(text_lines[start:end]))
        timestamps.append((ts_lines[start] + ts_lines[end - 1]) / 2)

    return windows, timestamps


def pearsonr_ci(x, y, ci=95, n_boots=10000, random_state=0):
    """
    Calculates the upper and lower bounds of the bootstrap-estimated
    confidence interval given by `ci` for the Pearson correlation
    coefficient.

    Parameters
    ----------
    x, y : array_like
        The two arrays of data to correlate.
    ci : float, optional
        The confidence interval to calculate, as a percentage (default:
        95).
    n_boots : int, optional
        The number of bootstrap samples to draw (default: 10,000).
    random_state : int or array_like, optional
        The random seed to use for reproducibility (default: 0). Must be
        convertible to 32-bit unsigned integer(s).

    Returns
    -------
    ci_low, ci_high : tuple of float
        The lower and upper bounds of the confidence interval.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    np.random.seed(random_state)

    # (n_boots, n_observations) paired arrays
    rand_ixs = np.random.randint(0, x.shape[0], size=(n_boots, x.shape[0]))
    x_boots = x[rand_ixs]
    y_boots = y[rand_ixs]

    # differences from mean
    x_mdiffs = x_boots - x_boots.mean(axis=1)[:, None]
    y_mdiffs = y_boots - y_boots.mean(axis=1)[:, None]

    # sums of squares
    x_ss = np.einsum('ij, ij -> i', x_mdiffs, x_mdiffs)
    y_ss = np.einsum('ij, ij -> i', y_mdiffs, y_mdiffs)

    # pearson correlations
    r_boots = np.einsum('ij, ij -> i', x_mdiffs, y_mdiffs) / np.sqrt(
        x_ss * y_ss)

    # upper and lower bounds for confidence interval
    ci_low = np.percentile(r_boots, (100 - ci) / 2)
    ci_high = np.percentile(r_boots, (ci + 100) / 2)
    return ci_low, ci_high


def preprocess_text(textlist, correction_counter=None):
    """
    Handles text preprocessing of lecture transcripts and quiz questions
    & answers. Performs case and whitespace normalization, punctuation
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
    textlist : sequence of str
        List of text samples (lecture transcript lines, quiz questions,
        or quiz answers) to be processed.
    correction_counter : `collections.defaultdict`, optional
        A `collections.defaultdict` instance with `default_factory=int`.
        Records detected "misses" by the `WordNetLemmatizer` (usually
        caused by the POS tagger mis-labeling a word) corrected by
        parsing the word's synset directly (via the `synset_match`
        function). If provided, keys of (word, lemma) will be added or
        incremented for each correction. Useful for spot-checking
        corrections to ensure only proper substitutions were made.

    Returns
    -------
    list of str
        The original `textlist` with preprocessing steps applied to each
        item.

    """
    if correction_counter is not None:
        if isinstance(correction_counter, defaultdict):
            if not correction_counter.default_factory is int:
                raise ValueError(
                    "'default_factory for 'correction_counter' must be 'int''"
                )
        else:
            raise TypeError(
                "'correction_counter' must be a 'collections.defaultdict' "
                "with 'default_factory=int'"
            )

    # define some constants only used in this function:
    lemmatizer = WordNetLemmatizer()
    # suffixes to look for when correcting lemmatization errors
    correctable_sfxs = ('s', 'ing', 'ly', 'ed', 'er', 'est')
    # corpus-specific words to exclude from lemma correction
    dont_lemmatize = ['stronger', 'strongest', 'strongly', 'especially']
    # POS tag mapping, format: {Treebank tag (1st letter only): Wordnet}
    tagset_mapping = defaultdict(
        lambda: 'n',   # defaults to noun
        {
            'N': 'n',  # noun types
            'P': 'n',  # pronoun types, predeterminers
            'V': 'v',  # verb types
            'J': 'a',  # adjective types
            'D': 'a',  # determiner
            'R': 'r'   # adverb types
        })

    # insert delimiters between text samples to map processed text back
    # to original chunk
    chunk_delimiter = 'chunkdelimiter'
    processed_chunks = [[] for _ in textlist]
    # clean spacing, normalize case, strip puncutation
    # (temporarily leave punctuation useful for POS tagging)
    full_text = f' {chunk_delimiter} '.join(textlist).lower()
    punc_stripped = re.sub("[^a-zA-Z\s']+", '', full_text.replace('-', ' '))
    # POS tagging (works better on full transcript, more context provided)
    words_tags = pos_tag(punc_stripped.split())

    chunk_ix = 0
    for word, tag in words_tags:
        if word == chunk_delimiter:
            # denotes end of a text chunk
            chunk_ix += 1
            continue

        # discard contraction clitics (always stop words or possessive)
        # irregular stems (don, isn, etc.) handled by stop word removal
        elif "'" in word:
            word = word.split("'")[0]
        # remove stop words & digits
        if word in STOP_WORDS or word[0].isdigit():
            continue

        if word not in dont_lemmatize:
            # convert Treebank POS tags to WordNet POS tags; lemmatize
            tag = tagset_mapping[tag[0]]
            lemma = lemmatizer.lemmatize(word, tag)

            # handles most cases where POS tagger misidentifies a word,
            # causing WordNet Morphy to use the wrong syntactic
            # transformation and fail
            if (
                    lemma == word and
                    any(word.endswith(sfx) for sfx in correctable_sfxs) and
                    len(word) > 4
            ):
                lemma = synset_match(word)
                if lemma != word and correction_counter is not None:
                    # record changes made this way to spot-check later
                    correction_counter[(word, lemma)] += 1
        else:
            lemma = word

        # place back in correct text chunk
        processed_chunks[chunk_ix].append(lemma)

    # join words within each chunk
    return [' '.join(c) for c in processed_chunks]


def r2z(r, fix_inf=False):
    """
    Computes the Fisher *z*-transformation.

    Parameters
    ----------
    r : scalar or numpy.ndarray
        Correlation value(s)
    fix_inf : bool, optional
        If `True`, replace  (+/-) `numpy.inf` values in the result with
        (+/-) 18.714973875118524. See Notes for more details.

    Returns
    -------
    zs : scalar or numpy.ndarray
        *z*-transformed correlation value(s)

    Notes
    -----
    Because the natural logarithm is undefined at 0, the Fisher
    *z*-transform returns (+/-) infinity for correlations of (+/-) 1.0.
    If `fix_inf` is passed, the function will replace infinite
    values in output the result of `r2z(1 - 1e-16)` (or
    `r2z(-1 + 1e-16)`), the closest possible 64-bit float to (+/1) 1.0.
    """
    zs = 0.5 * (np.log(1 + r) - np.log(1 - r))
    if fix_inf:
        # replace with r2z(1-1e-16) <-- closest possible float64 value
        # to 1
        zs[zs == np.inf] = 18.714973875118524
        zs[zs == -np.inf] = -18.714973875118524
    return zs


def rbf_sum(obs_coords, pred_coords, width, metric='euclidean'):
    """
    Given a set of observed coordinates and predicted coordinates,
    computes the (unweighted) sum of Gaussian radial basis functions
    centered on each observed coordinate, evaluated at each predicted
    coordinate.

    Parameters
    ----------
    obs_coords : numpy.ndarray
        An (x, z) array of coordinates for `x` nodes in `z` dimensions.
    pred_coords : numpy.ndarray
        A (y, z) array of `y` coordinates in `z` dimensions at which to
        evaluate the sum of RBFs.
    width : scalar
        The Width of the Gaussian kernel.
    metric : str or callable, optional
        The metric used to compute the pairwise distance between
        coordinates (default: `'euclidean'`, Euclidean distance). May be
        any named metric accepted by `scipy.spatial.distance.cdist` or a
        callable that takes two `array_like` arguments.

    Returns
    -------
    numpy.ndarray
        A 1-d array of summed RBFs evaluated at each coordinate given by
        `pred_coords`.
    """
    dmat = cdist(obs_coords, pred_coords, metric=metric)
    return np.exp(-dmat ** 2 / width).sum(axis=0)


def reconstruct_trace(lecture, questions, accuracy):
    """
    Reconstructs a participant's knowledge trace based on a lecture's
    trajectory (or any other set of coordinates), a set of questions'
    topic vectors, and binary accuracy scores for those questions.

    Parameters
    ----------
    lecture: numpy.ndarray
        `(n_coordinates, n_features)` matrix of coordinates for which to
        estimate knowledge.
    questions: numpy.ndarray
        `(n_observations, n_features)` matrix of coordinates for the
        quiz questions used to estimate knowledge for each of the
        `n_coordinates` locations.
    accuracy: array_like
        `(n_observations,)` binary array denoting whether each question
        was answered correctly (`True`|`1`) or incorrectly
        (`False`/`0`).
    """
    assert len(questions) == len(accuracy)
    acc = np.array(accuracy, dtype=bool)

    # compute timepoints by questions weights matrix
    wz = 1 - cdist(lecture, questions, metric='correlation')
    # normalize to be between 0 and 1
    wz -= wz.min()
    wz /= wz.max()
    # sum over questions (total possible weights for each timepoint)
    a = wz.sum(axis=1)
    # sum weights from correctly answered questions at each timepoint
    b = wz[:, acc].sum(axis=1)
    # divide weight from correct answers by total possible weight
    return b / a


def set_figure_style():
    """
    Sets some helpful `matplotlib`  options for figures generated for
    the paper. This gets called automatically whenever `khan_helpers` is
    imported, but occasionally needs to be called again manually when
    some other function has overwritten the relevant
    `matplotlib.rcParams` (e.g., inside `seaborn.axes_style` context
    managers).
    """
    # embed text in PDFs for illustrator
    plt.rcParams['pdf.fonttype'] = 42

    # use Myriad Pro font, if available
    if FONTS_DIR.is_dir() and next(FONTS_DIR.iterdir(), None) is not None:
        # check whether the font has already been loaded by
        # `matplotlib`'s font manager
        myriad_pro_fonts = [f for f in font_manager.fontManager.ttflist
                            if f.name == 'Myriad Pro']
        if len(myriad_pro_fonts) == 0:
            for font_file in font_manager.findSystemFonts(fontpaths=[FONTS_DIR]):
                font_manager.fontManager.addfont(font_file)

        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = (['Myriad Pro']
                                           + plt.rcParams['font.sans-serif'])


def show_source(obj):
    """
    Displays the source code for an object defined outside the current
    notebook.

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
    IPython.display.HTML or Object
        If `obj` is a code object, an `IPython.display.HTML` object.
        Otherwise, the original `obj`.
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


def synset_match(word, min_similarity=0.6):
    """
    Attempts to identify the proper lemma for a given `word`. Searches
    WordNet's database of cognitive synonyms for the provided `word`
    (its "synset") as well as the pertainyms of each word in the synset
    (to handle adverb-adjective relationships).

    Works based on the assumption that the correct lemma is the most
    similar choice (via `difflib.SequenceMatcher`) to the original word
    *that is also shorter than the original word*.

    Parameters
    ----------
    word : str
        The word to lemmatize.
    min_similarity : float, optional
        The minimum similarity to the provided word for a possible lemma
        to be considered correct (default: 0.6, inherited from default
        "`cutoff`" value for `difflib.get_close_matches()`).

    Returns
    -------
    str
        The lemma for the given `word`, if one was identified.
        Otherwise, the original `word`.
    """
    possible_matches = []
    for synset in wordnet.synsets(word):
        for lemma in synset.lemmas():
            possible_matches.append(lemma.name())
            for pert in lemma.pertainyms():
                possible_matches.append(pert.name())

    possible_matches = list(set(possible_matches))
    possible_matches = [m.lower() for m in possible_matches
                        if len(m) <= len(word)]
    # sort by similarity to word
    close_matches = get_close_matches(word,
                                      possible_matches,
                                      n=2,
                                      cutoff=min_similarity)
    if len(close_matches) == 0:
        return word
    # if original word was in synset lemmas and the second closest
    # possibility is shorter, use that
    elif (
            (close_matches[0] == word) and
            (len(close_matches) > 1) and
            (len(close_matches[1]) < len(word))
    ):
        return close_matches[1]
    else:
        return close_matches[0]


def z2r(z):
    """
    Computes the inverse Fisher *z*-transformation.

    Parameters
    ----------
    z : array_like
        *z*-transformed correlation value(s).

    Returns
    -------
    r : array_like
        Correlation value(s).
    """
    return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)

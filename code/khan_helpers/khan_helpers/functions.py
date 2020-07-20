import re
from datetime import timedelta
from inspect import getsource
from typing import Iterator

import numpy as np
from IPython.display import display, HTML
from IPython.core.oinspect import pylight
from scipy.interpolate import interp1d
from scipy.spatial.distance import cdist

from .constants import STOP_WORDS


def _ts_to_sec(ts):
    # converts timestamp of elapsed time from "MM:SS" format to scalar
    mins, secs = ts.split(':')
    return timedelta(minutes=int(mins), seconds=int(secs)).total_seconds()


def corr_mean(rs, axis=None):
    # computes the mean of correlation coefficients, performing the
    # Fisher z-transformation & inverse z-transformation before & after
    return z2r(np.nanmean([r2z(r) for r in rs], axis=axis))


def format_text(textlist, sw=STOP_WORDS):
    # some simple text preprocessing:
    # - removes punctuation & symbols
    # - normalizes everything to lowercase,
    # - splits hyphenated words, removes apostrophes
    clean_textlist = []
    for chunk in textlist:
        no_punc = re.sub("[^a-zA-Z\s'-]+", '', chunk.lower()).replace('-', ' ')
        no_stop = ' '.join([word for word in no_punc.split() if word not in sw])
        clean_text = re.sub("'+", '', no_stop)
        clean_textlist.append(clean_text)

    return clean_textlist


def rbf(obs_coords, pred_coords, width, metric='euclidean'):
    return np.exp(-cdist(obs_coords, pred_coords, metric=metric) ** 2 / width)


def rbf_interp(obs_coords, obs_vals, pred_coords, width, metric='euclidean'):
    weights = rbf(obs_coords, pred_coords, width=width, metric=metric)
    return (weights.T * obs_vals).sum(axis=1) / weights.sum(axis=0)


def interp_lecture(lec_traj, timestamps):
    # interpolates lecture trajectories to 1 vector per second
    new_tpts = np.arange(timestamps[-1])
    interp_func = interp1d(timestamps, lec_traj, axis=0)
    return interp_func(new_tpts)


def multicol_display(*outputs,
                     ncols=2,
                     col_headers=None,
                     table_css=None,
                     header_css=None,
                     row_css=None,
                     cell_css=None):
    """
    Renders notebook cell output in multiple side-by-side columns using
    an HTML table element. The resulting table looks similar to the HTML
    output of `pandas.DataFrame.to_html. Accepts a variable number of
    output items, and creates multiple rows if len(outputs) > ncols.

    *outputs:     (positional args) The objects to be placed in each
                  cell of the table. May be any Python class that defines
                  a __str__ and/or __repr__ method
    ncols:        (int; default: 2) The number of columns for the display.
                  If the number of outputs passed is greater than ncols,
                  the display will include multiple rows
    col_headers:  (list-like; optional) Content to fill the table header
                  (<th>) element for each column. If passed, must have a
                  length of ncols.
    table_css:    (dict; optional) Additional CSS properties to be applied
                  to the outermost table (<table>) element. For simplicity,
                  these are passed to the .style HTML attribute.
    header_css:   (dict; optional) Analogous to `table_css`, but specifies
                  properties passed to each table header (<th>) element.
    row_css:      (dict; optional) Analogous to `table_css`, but specifies
                  properties passed to each table row (<tr>) element.
    cell_css:     (dict; optional) Analogous to `table_css`, but specifies
                  properties passed to each table cell (<td>) element.
    """
    def _fmt_python_types(obj):
        # formats some common Python objects for display
        if isinstance(obj, str):
            return obj.replace('\n', '<br>')
        elif (isinstance(obj, (list, tuple, set, Iterator))
              or type(obj).__module__ == 'numpy'):
            return ', '.join(obj)
        elif isinstance(obj, dict):
            return '<br><br>'.join(f'<b>{k}</b>:&emsp;{_fmt_python_types(v)}'
                                   for k, v in obj.items())
        else:
            return obj

    outs_fmt = []
    for out in outputs:
        outs_fmt.append(_fmt_python_types(out))
    if col_headers is None:
        col_headers = []
    else:
        assert hasattr(col_headers, '__iter__') and len(col_headers) == ncols

    # coerce to proper types for string replacement
    table_css = {} if table_css is None else table_css
    header_css = {} if header_css is None else header_css
    row_css = {} if row_css is None else row_css
    cell_css = {} if cell_css is None else cell_css

    table_css = ";".join(f"{prop}:{val}" for prop, val in table_css.items())
    header_css = ";".join(f"{prop}:{val}" for prop, val in header_css.items())
    row_css = ";".join(f"{prop}:{val}" for prop, val in row_css.items())
    cell_css = ";".join(f"{prop}:{val}" for prop, val in cell_css.items())

    # individual element templates with some reasonable pre-set style properties
    html_table = f"<table style='width:100%; border:0px;{table_css}'>{{header}}{{content}}</table>"
    html_header = f"<th style='border:0px;{header_css}'>{{content}}</th>"
    html_row = f"<tr style='border:0px;{row_css}'>{{content}}</tr>"
    html_cell = f"<td style='width:{100 / ncols}%;vertical-align:top;border:0px;{cell_css}'>{{content}}</td>"

    # deal with HTML formatting and substitutions from style dicts
    headers = [html_header.format(content=h) for h in col_headers]
    cells = [html_cell.format(content=out) for out in outs_fmt]
    cells.extend([html_cell.format(content="")] * (ncols - len(outs_fmt) % ncols))
    header_row = html_row.format(content="".join(headers))
    rows = [html_row.format(content="".join(cells[i: i + ncols])) for i in range(0, len(cells), ncols)]
    # render notebook display cell
    display(HTML(html_table.format(header="".join(headers), content="".join(rows))))


def parse_windows(transcript, wsize):
    # formats lecture transcripts as overlapping sliding windows
    # to feed as documents to topic model
    # also returns timestamps of transcribed speech for interpolation
    lines = transcript.splitlines()
    text_lines = [l for ix, l in enumerate(lines) if ix % 2]
    ts_lines = [_ts_to_sec(l) for ix, l in enumerate(lines) if not ix % 2]
    windows = []
    timestamps = []
    for ix in range(1, wsize):
        start, end = 0, ix
        windows.append(' '.join(text_lines[start: end]))
        timestamps.append((ts_lines[start] + ts_lines[end - 1]) / 2)

    for ix in range(len(ts_lines)):
        start = ix
        end = ix + wsize if ix + wsize <= len(text_lines) else len(text_lines)
        windows.append(' '.join(text_lines[start: end]))
        timestamps.append((ts_lines[start] + ts_lines[end - 1]) / 2)

    return windows, timestamps


def r2z(r):
    # computes the Fisher z-transformation
    with np.errstate(invalid='ignore', divide='ignore'):
        return 0.5 * (np.log(1 + r) - np.log(1 - r))


def show_source(obj):
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


def z2r(z):
    # computes the inverse Fisher z-transformation
    with np.errstate(invalid='ignore', divide='ignore'):
        return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)
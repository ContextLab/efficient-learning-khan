import re
import numpy as np
from datetime import timedelta
from inspect import getsource
from pathlib import Path
from IPython.display import HTML
from IPython.core.oinspect import pylight
from nltk.corpus import stopwords
from scipy.interpolate import interp1d
from scipy.stats import entropy


##########################################
#            REUSED VARIABLES            #
##########################################
DATA_DIR = Path('/mnt/data')
RAW_DIR = DATA_DIR.joinpath('raw')
PARTICIPANTS_DIR = DATA_DIR.joinpath('participants')
TRAJS_DIR = DATA_DIR.joinpath('trajectories')
EMBS_DIR = DATA_DIR.joinpath('embeddings')
MODELS_DIR = DATA_DIR.joinpath('models')
FIG_DIR = Path('/mnt/paper/figs/')
N_PARTICIPANTS = 50
LECTURE_WSIZE = 20
STOP_WORDS = stopwords.words('english') + ["even", "i'll", "i'm", "let", "let's",
                                           "really", "they'd", "they're",
                                           "they've", "they'll", "that's"]


##########################################
#            REUSED FUNCTIONS            #
##########################################
def _ts_to_sec(ts):
    # converts timestamp of elapsed time from "MM:SS" format to scalar
    mins, secs = ts.split(':')
    return timedelta(minutes=int(mins), seconds=int(secs)).total_seconds()


def corr_mean(rs, axis=0):
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


def interp_lecture(lec_traj, timestamps):
    # interpolates lecture trajectories to 1 vector per second
    new_tpts = np.arange(timestamps[-1])
    interp_func = interp1d(timestamps, lec_traj, axis=0)
    return interp_func(new_tpts)


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


def symmetric_kl(a, b, c=1e-11):
    # symmetrized KL divergence
    return np.divide(entropy(a + c, b + c) + entropy(b + c, a + c), 2)


def z2r(z):
    # computes the inverse Fisher z-transformation
    with np.errstate(invalid='ignore', divide='ignore'):
        return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)

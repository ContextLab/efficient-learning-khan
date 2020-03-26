import re
import numpy as np
from datetime import timedelta
from inspect import getsource
from os.path import join as opj
from IPython.display import HTML
from IPython.core.oinspect import pylight
from nltk.corpus import stopwords
from scipy.interpolate import interp1d
from scipy.stats import entropy


##########################################
#            REUSED VARIABLES            #
##########################################
DATA_DIR = '/mnt/data'
RAW_DIR = opj(DATA_DIR, 'raw')
PARTICIPANTS_DIR = opj(DATA_DIR, 'participants')
TRAJS_DIR = opj(DATA_DIR, 'trajectories')
EMBS_DIR = opj(DATA_DIR, 'embeddings')
MODELS_DIR = opj(DATA_DIR, 'models')
FIG_DIR = '/mnt/paper/figs/'
N_PARTICIPANTS = 50
LECTURE_WSIZE = 15
STOP_WORDS = stopwords.words('english') + ["even", "I'll", "I'm", "let", "let's",
                                           "really", "they'd", "they're",
                                           "they've", "they'll", "that's"]


##########################################
#            REUSED FUNCTIONS            #
##########################################
def _ts_to_sec(ts):
    # converts timestamp of elapsed time
    # from "MM:SS" format to scalar
    mins, secs = ts.split(':')
    mins, secs = int(mins), int(secs)
    return timedelta(minutes=mins, seconds=secs).total_seconds()


def format_text(textlist, sw=STOP_WORDS):
    # some simple text preprocessing:
    # removes punctuation & symbols, converts to all lowercase,
    # splits hyphenated words, removes apostrophes
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


def show_source(obj):
    try:
        src = getsource(obj)
    except TypeError as e:
        # if called on variable, just show its value
        src = obj
    try:
        return HTML(pylight(src))
    except AttributeError:
        # pylight doesn't work on certain types
        return src


def symmetric_kl(a, b, c=1e-11):
    # symmetrized KL divergence
    return np.divide(entropy(a + c, b + c) + entropy(b + c, a + c), 2)

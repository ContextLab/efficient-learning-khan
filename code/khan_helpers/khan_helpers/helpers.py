import re
import numpy as np
from datetime import timedelta
from inspect import getsource, isclass, isfunction
from os.path import join as opj
from nltk.corpus import stopwords
from scipy.stats import entropy


##########################################
#            REUSED VARIABLES            #
##########################################
DATA_DIR= '/mnt/data'
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


def show_source(obj):
    try:
        getsource(obj)
    except TypeError as e:
        if not (isclass(obj) or isfunction(obj)):
            return obj
        else:
            raise ValueError("Couldn't identify source of object") from e


def symmetric_kl(a, b, c=1e-11):
    # symmetrized KL divergence
    return np.divide(entropy(a + c, b + c) + entropy(b + c, a + c), 2)

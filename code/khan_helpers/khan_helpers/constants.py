from pathlib import Path

from nltk.corpus import stopwords


DATA_DIR = Path('/mnt/data')
RAW_DIR = DATA_DIR.joinpath('raw')
PARTICIPANTS_DIR = DATA_DIR.joinpath('participants')
TRAJS_DIR = DATA_DIR.joinpath('trajectories')
EMBS_DIR = DATA_DIR.joinpath('embeddings')
MODELS_DIR = DATA_DIR.joinpath('models')
FIG_DIR = Path('/mnt/paper/figs/')

# number of timestamped lines in lecture transcript sliding windows
LECTURE_WSIZE = 30

# standard English stop words + some corpus-specific words
STOP_WORDS = stopwords.words('english') + ['actual', 'actually', 'also', 'bit',
                                           'could', 'e', 'even', 'first',
                                           'four', 'let', 'like', 'mc',
                                           'really', 'saw', 'see', 'seen',
                                           'thing', 'things', 'two', 'follow',
                                           'following']

FORCES_LECTURE_COLOR = '#3f54a5'
BOS_LECTURE_COLOR = '#0f8140'
FORCES_QUESTION_COLOR = '#7d9ed2'
BOS_QUESTION_COLOR = '#70c167'
GENERAL_QUESTION_COLOR = '#b96bac'

WORDLE_COLORS = ('#ffde17', '#ec008c', '#f26522')

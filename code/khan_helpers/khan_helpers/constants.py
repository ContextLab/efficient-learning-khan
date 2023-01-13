from pathlib import Path

from nltk.corpus import stopwords


########################################
#                PATHS                 #
########################################

DATA_DIR = Path('/mnt/data')
RAW_DIR = DATA_DIR.joinpath('raw')
PARTICIPANTS_DIR = DATA_DIR.joinpath('participants')
TRAJS_DIR = DATA_DIR.joinpath('trajectories')
EMBS_DIR = DATA_DIR.joinpath('embeddings')
MODELS_DIR = DATA_DIR.joinpath('models')
FIG_DIR = Path('/mnt/paper/figs/')


########################################
#           MODEL PARAMETERS           #
########################################

# standard English stop words + some corpus-specific words
STOP_WORDS = stopwords.words('english') + ['actual', 'actually', 'also', 'bit',
                                           'could', 'e', 'even', 'first',
                                           'four', 'let', 'like', 'mc',
                                           'really', 'saw', 'see', 'seen',
                                           'thing', 'things', 'two', 'follow',
                                           'following']

# corpus-specific words to exclude from WordNet-based lemmatization
DONT_LEMMATIZE = ['stronger', 'strongest', 'strongly', 'especially']

# CountVectorizer parameters
CV_PARAMS = {
    'strip_accents': 'unicode',
    'stop_words': None  # stop words removed during text preprocessing
}

# LatentDirichletAllocation parameters
LDA_PARAMS = {
    'n_components': 15,
    'learning_method': 'batch',
    'random_state': 0
}

# UMAP embedding parameters
UMAP_PARAMS = {
    'n_components': 2,
    'n_neighbors': 15,
    'min_dist': 0.1,
    'spread': 1.0,
    'random_state': 0
    # TODO: add metric=correlation_exp
}


########################################
#                OTHERS                #
########################################

# number of participants in dataset
N_PARTICIPANTS = 50

# number of timestamped lines in lecture transcript sliding windows
LECTURE_WSIZE = 30

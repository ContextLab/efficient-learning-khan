from pathlib import Path

from nltk.corpus import stopwords


##########################################
#                 PATHS                  #
##########################################
DATA_DIR = Path('/mnt/data')
RAW_DIR = DATA_DIR.joinpath('raw')
PARTICIPANTS_DIR = DATA_DIR.joinpath('participants')
TRAJS_DIR = DATA_DIR.joinpath('trajectories')
EMBS_DIR = DATA_DIR.joinpath('embeddings')
MODELS_DIR = DATA_DIR.joinpath('models')
FIG_DIR = Path('/mnt/paper/figs/')

##########################################
#            MODEL PARAMETERS            #
##########################################
# CountVectorizer parameters
STOP_WORDS = stopwords.words('english') + ["even", "i'll", "i'm", "let", "let's",
                                           "really", "they'd", "they're",
                                           "they've", "they'll", "that's"]
CV_PARAMS = {
    'strip_accents': 'unicode',
    'stop_words': STOP_WORDS
}

# LatentDirichletAllocation parameters
LDA_PARAMS = {
    'n_components': 10,
    'learning_method': 'batch',
    'random_state': 0
}

# UMAP embedding parameters
UMAP_PARAMS = {
    'n_components': 2,
    'n_neighbors': 15,
    'min_dist': 0.8,
    'spread': 1.0,
    'random_state': 0
}


##########################################
#                 OTHERS                 #
##########################################
# number of participants in dataset
N_PARTICIPANTS = 50

# number of timestamped lines in lecture transcript sliding windows
LECTURE_WSIZE = 20

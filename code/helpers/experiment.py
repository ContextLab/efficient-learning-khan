import numpy as np
import pandas as pd
from os.path import join as opj
from nltk.corpus import stopwords

DATADIR= '../../data'
RAWDIR = opj(DATADIR, 'raw')
TRAJS_DIR = opj(DATADIR, 'trajectories')
MODELS_DIR = opj(DATADIR, 'models')


class Experiment:
    def __init__(self):
        self.lectures = ['Four Forces', 'Birth of Stars']
        self.lecture_wsize = 15
        self.stop_words = stopwords.words('english') + ["let", "let's", "they'd",
                                                        "they're", "they've",
                                                        "they'll", "that's",
                                                        "I'll", "I'm"]
        self.cv_params = {
            'max_df': 0.95,
            'min_df': 2,
            'max_features': 500,
            'stop_words': self.stop_words
        }
        self.lda_params = {
            'n_components': 20,
            'learning_method': 'batch',
            'random_state': 0
        }
        self.ff_transcript = None
        self.bos_transcript = None
        self.questions = None
        self.forces_windows = None
        self.bos_windows = None
        self.forces_traj = None
        self.bos_traj = None
        self.question_vectors = None

    def load_transcript(self, lecture):
        if lecture not in ('forces', 'bos'):
            raise ValueError("lecture may be one of: 'forces', 'bos'")
        path = opj(RAWDIR, f'{lecture}_transcript_timestamped.txt')
        with open(path, 'r') as f:
            transcript = f.read()
        if lecture == 'forces':
            self.ff_transcript = transcript
        else:
            self.bos_transcript = transcript

    def load_questions(self):
        path = opj(RAWDIR, 'questions.tsv')
        self.questions = pd.read_csv(path,
                                     sep='\t',
                                     names=['index', 'lecture', 'questions',
                                            'A', 'B', 'C', 'D'],
                                     index_col='index')

    def load_lecture_trajs(self):
        self.forces_traj = np.load(opj(TRAJS_DIR, 'forces_lecture.npy'))
        self.bos_traj = np.load(opj(TRAJS_DIR, 'bos_lecture.npy'))

    def load_question_vectors(self):
        






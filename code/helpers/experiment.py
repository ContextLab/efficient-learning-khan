import hypertools as hyp
import numpy as np
import pandas as pd
from os.path import join as opj
from nltk.corpus import stopwords

DATADIR= '../../data'
RAWDIR = opj(DATADIR, 'raw')
TRAJS_DIR = opj(DATADIR, 'trajectories')
MODELS_DIR = opj(DATADIR, 'models')
STOP_WORDS = stopwords.words('english') + ["let", "let's", "they'd",
                                           "they're", "they've", "they'll",
                                           "that's", "I'll", "I'm"]


class Experiment:
    def __init__(self):
        self.lectures = ['Four Forces', 'Birth of Stars']
        self.forces_transcript = None
        self.bos_transcript = None
        self.questions = None
        self.forces_windows = None
        self.bos_windows = None
        self.forces_traj = None
        self.bos_traj = None
        self.question_vectors = None
        self.answer_vectors = None
        self.cv = None
        self.lda = None
        self.lecture_wsize = 15
        self.cv_params = {
            'max_df': 0.95,
            'min_df': 2,
            'max_features': 500,
            'stop_words': STOP_WORDS
        }
        self.lda_params = {
            'n_components': 20,
            'learning_method': 'batch',
            'random_state': 0
        }

    def get_lecture_traj(self, lecture):
        if lecture in ['forces', 1]:
            return self.forces_traj
        elif lecture in ['bos', 2]:
            return self.bos_traj
        else:
            raise ValueError("Lecture should be either 1, 'forces', 2, or 'bos'")

    def get_question_vecs(self, qids=None, lectures=None):
        # get question topic vectors by question ID(s) or lecture(s)
        if (qids is lectures is None) or (qids is not None and lectures is not None):
            raise ValueError("must pass either qids or lecture (not both)")
        if lectures is not None:
            qids = []
            if 'forces' in lectures:
                qids += list(range(15))
            if 'bos' in lectures:
                qids += list(range(16, 30))
            if 'general' in lectures:
                qids += list(range(30, 39))
        return self.question_vectors[qids]

    def plot(self, lectures=None, questions=None, participants=None, keys=None, **kwargs):
        # wraps hypertools.plot for multisubject plots
        # plots in order: [lectures, questions, participants[0][keys[0]], participants[0][keys[1]], etc
        if lectures is None:
            lectures = []
        if questions is None:
            questions = []
        elif isinstance(questions, (str, int)):
            questions = [questions]
        if participants is None:
            participants = []
        if len(participants) > 0 and keys is None:
            raise ValueError("Must pass keys if passing participants")

        to_plot = [self.get_lecture_traj(l) for l in lectures]
        if len(questions) > 0:
            if isinstance(questions[0], str):
                to_plot += self.get_question_vecs(lecture=questions)
            else:
                to_plot += self.get_question_vecs(qids=questions)
        to_plot += [p.traces[key] for p in participants for key in keys]
        return hyp.plot(to_plot, **kwargs)

    # data loaders
    def load_transcript(self, lecture):
        if lecture not in ('forces', 'bos'):
            raise ValueError("lecture may be one of: 'forces', 'bos'")
        path = opj(RAWDIR, f'{lecture}_transcript_timestamped.txt')
        with open(path, 'r') as f:
            transcript = f.read()
        if lecture == 'forces':
            self.forces_transcript = transcript
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
        self.question_vectors = np.load(opj(TRAJS_DIR, 'all_questions.npy'))

    def load_answer_vectors(self):
        self.answer_vectors = np.load(opj(TRAJS_DIR, 'all_answers.npy'))

    def load_windows(self, lecture):
        if lecture not in ('forces', 'bos'):
            raise ValueError("lecture may be one of: 'forces', 'bos'")
        windows = np.load(opj(RAWDIR, f'{lecture}_transcript_timestamped.txt'))
        if lecture == 'forces':
            self.forces_windows = windows
        else:
            self.bos_windows = windows

    def load_cv(self):
        self.cv = np.load(opj(MODELS_DIR, 'fit_CV.npy'), allow_pickle=True).item()

    def load_lda(self):
        self.lda = np.load(opj(MODELS_DIR, 'fit_LDA.npy'), allow_pickle=True).item()

import pickle

import numpy as np
import pandas as pd
from PIL.Image import open as open_image

from .constants import (
    DATA_DIR,
    EMBS_DIR,
    MODELS_DIR,
    PARTICIPANTS_DIR,
    RAW_DIR,
    TRAJS_DIR,
    N_PARTICIPANTS,
)
from .functions import _ts_to_sec


class LazyLoader:
    # Descriptor class that handles deferred loading and caching of data
    def __init__(self, loader, *loader_args, **loader_kwargs):
        self.loader = loader
        self.loader_args = loader_args
        self.loader_kwargs = loader_kwargs

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, owner=None):
        obj.__dict__[self.name] = getattr(obj, self.loader)(*self.loader_args, **self.loader_kwargs)
        return obj.__dict__[self.name]


class Experiment:
    participants = LazyLoader('_load_participants')
    avg_participant = LazyLoader('_load_avg_participant')

    forces_transcript = LazyLoader('_load_transcript', 'forces')
    bos_transcript = LazyLoader('_load_transcript', 'bos')
    questions = LazyLoader('_load_questions')

    forces_windows = LazyLoader('_load_windows', 'forces')
    bos_windows = LazyLoader('_load_windows', 'bos')

    forces_timestamps = LazyLoader('_load_timestamps', 'forces')
    bos_timestamps = LazyLoader('_load_timestamps', 'bos')

    forces_traj = LazyLoader('_load_topic_vectors', 'forces')
    bos_traj = LazyLoader('_load_topic_vectors', 'bos')
    question_vectors = LazyLoader('_load_topic_vectors', 'questions')
    answer_vectors = LazyLoader('_load_topic_vectors', 'answers')

    forces_embedding = LazyLoader('_load_embedding', 'forces')
    bos_embedding = LazyLoader('_load_embedding', 'bos')
    question_embeddings = LazyLoader('_load_embedding', 'questions')

    fit_cv = LazyLoader('_load_fit_model', 'CV')
    fit_lda = LazyLoader('_load_fit_model', 'LDA')
    fit_umap = LazyLoader('_load_fit_model', 'UMAP')

    wordle_mask = LazyLoader('_load_wordle_mask')

    @property
    def all_data(self):
        return pd.concat(map(lambda p: p.data, self.participants),
                         keys=map(str, self.participants))

    def get_lecture_traj(self, lecture):
        if hasattr(lecture, '__iter__') and not isinstance(lecture, str):
            if len(lecture) > 1:
                return [self.get_lecture_traj(l) for l in lecture]
            else:
                return self.get_lecture_traj(lecture[0])
        elif lecture in ('forces', 1):
            return self.forces_traj
        elif lecture in ('bos', 2):
            return self.bos_traj
        else:
            raise ValueError('`lecture` should be either 1, "forces", 2, or "bos"')

    def get_question_vecs(self, qids=None, lectures=None):
        # get question topic vectors by question ID(s) or lecture(s)
        if (qids is lectures is None) or (qids is not None and lectures is not None):
            raise ValueError("must pass either `qids` or `lecture` (not both)")
        if lectures is not None:
            qids = []
            if 'forces' in lectures:
                qids.extend(range(15))
            if 'bos' in lectures:
                qids.extend(range(15, 30))
            if 'general' in lectures:
                qids.extend(range(30, 39))
        else:
            qids = [qid - 1 for qid in qids]
        return self.question_vectors[qids]

    def get_timepoint_text(self, lecture, timepoint, buffer=15):
        # TODO: map backwards through window timepoints rather than
        #  directly to transcript for more accuracy?
        if lecture == 'forces':
            transcript = self.forces_transcript
        elif lecture == 'bos':
            transcript = self.bos_transcript
        else:
            raise ValueError("Lecture must be either 'forces' or 'bos'")

        # get timestamps and text from transcript
        transcript = transcript.splitlines()
        timestamps = np.fromiter(map(_ts_to_sec, transcript[::2]), dtype=np.int16)
        text = np.array(transcript[1::2])
        # compute start and end time from timepoint and buffer
        onset, offset = timepoint - buffer, timepoint + buffer
        # make sure times are within bounds
        if onset < 0:
            onset = 0
        if offset > timestamps[-1]:
            offset = timestamps[-1]
        # get timestamps of text between those times
        text_ixs = np.where((timestamps >= onset) & (timestamps < offset))[0]
        return ' '.join(text[text_ixs])

    # TODO: delete if not used
    def save_participants(self, filepaths=None, allow_overwrite=False):
        to_save = list(self.participants)
        if 'avg_participant' in self.__dict__:
            to_save.append(self.avg_participant)
        if filepaths is None:
            filepaths = [None] * len(to_save)
        elif len(filepaths) != len(to_save):
            msg = "`filepaths` must contain one path per participant"
            if self.avg_participant is not None:
                msg += " (including average participant, last)"
            raise ValueError(msg)
        for p, fpath in zip(to_save, filepaths):
            p.save(filepath=fpath, allow_overwrite=allow_overwrite)

    ##########################################
    #              DATA LOADERS              #
    ##########################################
    def _load_participants(self):
        participants = []
        for pid in range(1, N_PARTICIPANTS + 1):
            path = PARTICIPANTS_DIR.joinpath(f'P{pid}.p')
            participants.append(pickle.loads(path.read_bytes()))
        return np.array(participants)

    def _load_avg_participant(self):
        path = PARTICIPANTS_DIR.joinpath('avg.p')
        return pickle.loads(path.read_bytes())

    def _load_transcript(self, lecture):
        path = RAW_DIR.joinpath(f'{lecture}_transcript_timestamped.txt')
        with path.open() as f:
            return f.read()

    def _load_questions(self):
        path = RAW_DIR.joinpath('questions.tsv')
        return pd.read_csv(path,
                           sep='\t',
                           names=['index', 'lecture', 'question', 'A', 'B', 'C', 'D'],
                           index_col='index')

    def _load_windows(self, lecture):
        return np.load(RAW_DIR.joinpath(f'{lecture}_windows.npy'))

    def _load_timestamps(self, lecture):
        return np.load(RAW_DIR.joinpath(f'{lecture}_timestamps.npy'))

    def _load_topic_vectors(self, file_key):
        filename_map = {
            'forces': 'forces_lecture',
            'bos': 'bos_lecture',
            'questions': 'all_questions',
            'answers': 'all_answers'
        }
        return np.load(TRAJS_DIR.joinpath(f'{filename_map[file_key]}.npy'))

    def _load_embedding(self, file_key):
        filename_map = {
            'forces': 'forces_lecture',
            'bos': 'bos_lecture',
            'questions': 'questions',
        }
        return np.load(EMBS_DIR.joinpath(f'{filename_map[file_key]}.npy'))

    def _load_fit_model(self, model):
        return np.load(MODELS_DIR.joinpath(f'fit_{model}.npy'), allow_pickle=True).item()

    def _load_wordle_mask(self):
        return np.array(open_image(DATA_DIR.joinpath('wordle-mask.jpg')))

import numpy as np
import pandas as pd
from ast import literal_eval
from html import unescape
from scipy.spatial.distance import cdist
from scipy.stats import entropy
from .experiment import Experiment

QS_PATH = '../../data/raw/questions.tsv'
TRAJS_DIR = '../../data/trajectories/'


class Participant(Experiment):
    def __init__(self, subID, psiturk_data=None, data_df=None):
        if (
            (psiturk_data is data_df is None)
            or (psiturk_data is not None and data_df is not None)
        ):
            raise ValueError("Must create Participant with either raw PsiTurk data OR a Pandas.DataFrame")
        if psiturk_data:
            self.raw_data = literal_eval(psiturk_data['datastring'])
            self.uniqueid = psiturk_data['uniqueid']
            self.date_collected = psiturk_data['beginhit'].split()[0]
            self.data = self._grade()
        elif data_df:
            fallback_msg = "Only set for participant created from raw PsiTurk data"
            self.raw_data = self.uniqueid = self.date_collected = fallback_msg
            self.data = data_df

        self.subID = subID
        self.traces = {}

    def __repr__(self):
        return self.data

    def __str__(self):
        print(f"Participant object with subID {self.subID}")

    def get_data(self, qset=None, lecture=None):
        # return (a subset of) the subject's data
        if isinstance(qset, int):
            qset = [qset]
        if isinstance(lecture, int):
            lecture = [lecture]

        d = self.data
        if qset is not None:
            d = d.loc[d['set'].isin(qset)]
        if lecture is not None:
            d = d.loc[d['lecture'].isin(lecture)]
        return d

    def store_trace(self, trace, store_key, overwrite=False):
        if not overwrite and store_key in self.traces:
            raise KeyError(f"{store_key} already stored for {str(self)}")
        self.traces[store_key] = trace


    def reconstruct_trace(self, qset=None, lecture=None, store=False, store_key=None):
        def symmetric_KL(a, b, c=1e-11):
            np.divide(entropy(a + c, b + c) + entropy(b + c, a + c), 2)

        lecture_traj =

        # compute timepoints by questions correlation matrix
        wz = 1 - cdist(lecture_traj, questions_model, metric=symmetric_KL)





    @property
    def all_questions(self, questions_path=QS_PATH):
        return pd.read_csv(questions_path,
                           sep='\t',
                           names=['index', 'video', 'question',
                                  'A', 'B', 'C', 'D'],
                           index_col='index')

    def _grade(self):
        # grades raw data and sets self.data
        data = []
        question_blocks = (3, 8, 13)
        all_qs = self.all_questions
        for set_num, qblock in enumerate(question_blocks):
            question_block = self.raw_data[qblock]['trialdata']
            answer_block = literal_eval(self.raw_data[qblock + 1]['trialdata']['responses'])
            for q_num, q in enumerate(question_block):
                # deal with HTML characters
                q_text = unescape(q['prompt'])
                # match question text to question in dataset
                q_info = all_qs.loc[all_qs.question == q_text]
                # error on failure to match questions
                if not q_info.values.any():
                    raise KeyError(f"failed to find question matching {q_text}")
                # set qID and reference lecture
                qid = q_info.index[0]
                lec = q_info.loc[qid, 'video']
                # get answer
                ans_text = answer_block[f'Q{q_num}']
                # error on failure to match question or unexpected letter
                try:
                    ans_let = q_info.squeeze()[q_info.squeeze() == ans_text].index[0]
                except IndexError as e:
                    raise KeyError(f"failed to find answer matching{ans_text}") from e
                assert ans_let in 'ABCD', f"found answer code {ans_let}, expected one of: 'A', 'B', 'C', 'D'"
                # set accuracy for response
                acc = 1 if ans_let == 'A' else 0
                data.append([qid, acc, set_num, lec])
        return pd.DataFrame(data, columns=['qID', 'accuracy', 'qset', 'lecture'])

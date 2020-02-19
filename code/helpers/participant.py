import numpy as np
import pandas as pd
import hypertools as hyp
from ast import literal_eval
from html import unescape
from scipy.spatial.distance import cdist
from scipy.stats import entropy


class Participant:
    def __init__(self, subid, data=None, raw_data=None, date_collected=None):
        self.subID = subid
        self.data = data
        fallback_msg = "Attribute only set for participant created from raw PsiTurk data"
        if raw_data is None:
            self.raw_data = fallback_msg
        else:
            self.raw_data = raw_data
        if date_collected is None:
            self.date_collected = fallback_msg
        else:
            self.date_collected = date_collected
        self.traces = {}

    @classmethod
    def from_psiturk(cls, psiturk_data, subid):
        raw_data = literal_eval(psiturk_data['datastring'])
        date_collected = psiturk_data['beginhit'].split()[0]
        p = cls(subid=subid, raw_data=raw_data, date_collected=date_collected)
        p.data = p._grade()
        return p

    def _repr_html_(self):
        # for displaying in Jupyter (IPython) notebooks
        print(self.__str__())
        try:
            return self.data.to_html()
        except AttributeError:
            return "Individual data unavailable"

    def __str__(self):
        return f"Participant {self.subID}"

    def __eq__(self, other):
        return self.subID == other

    def head(self, *args, **kwargs):
        print(self.__str__())
        return self.data.head(*args, **kwargs)

    def get_data(self, qset=None, lecture=None):
        # return (a subset of) the subject's data
        lec_keys = {'general': 0, 'forces': 1, 'bos': 2}
        if isinstance(qset, int):
            qset = [qset]
        # funnel ints, strings, lists of either into list of ints
        if isinstance(lecture, int):
            lecture = [lecture]
        elif isinstance(lecture, str):
            lecture = [lec_keys[lecture]]
        elif hasattr(lecture, '__iter__'):
            for l in range(len(lecture)):
                if isinstance(lecture[l], str):
                    lecture[l] = lec_keys[lecture[l]]

        d = self.data
        if qset is not None:
            d = d.loc[d['qset'].isin(qset)]
        if lecture is not None:
            d = d.loc[d['lecture'].isin(lecture)]
        return d

    def store_trace(self, trace, store_key):
        self.traces[store_key] = trace

    def reconstruct_trace(self, exp, lecture, qset=None, store=None, recon_lec=None):
        """
        Reconstructs a participant's memory trace based on a lecture's
        trajectory, a set of questions' topic vectors, and binary accuracy scores
        :param exp: (Experiment object) Used to access lecture trajectory and
                    question topic vectors
        :param lecture: (int, str, list-like of ints/strs) The lecture(s) for
                        which to get questions and scores
        :param qset: (int or list-like of ints) The question set for which to get
                     questions and scores. If [default] None, get data for all question sets
        :param store: (str) The key under which the reconstructed trace should be
                       stored in self.traces. If [default] None, don't store the trace
        :param recon_lec: (int or str) The lecture trajectory to use in reconstructing
                          the trace. Useful if passing an iterable to lecture in
                          order to get questions related to multiple lectures
        :return trace: (numpy.ndarray) The reconstructed memory trace
        """
        def symmetric_KL(a, b, c=1e-11):
            return np.divide(entropy(a + c, b + c) + entropy(b + c, a + c), 2)

        data = self.get_data(qset=qset, lecture=lecture)
        acc = data['accuracy'].tolist()
        qids = data['qID'].tolist()
        question_vecs = exp.get_question_vecs(qids=qids)
        if isinstance(lecture, (int, str)):
            lecture_traj = exp.get_lecture_traj(lecture)
        elif hasattr(lecture, '__iter__'):
            if recon_lec is not None:
                lecture_traj = exp.get_lecture_traj(recon_lec)
            else:
                raise ValueError("Must specify recon_lec if passing multiple lectures")
        else:
            raise ValueError("lecture should be one of: str, int, list-like of str/int")

        # compute timepoints by questions correlation matrix
        wz = 1 - cdist(lecture_traj, question_vecs, metric=symmetric_KL)
        # normalize
        wz -= np.min(wz)
        wz /= np.max(wz)
        # sum over questions
        a = np.sum(wz, axis=1)
        # sum over correctly answered questions
        b = np.sum(wz[:, list(map(bool, acc))], axis=1)
        # divide b by a
        b_a = np.array(np.divide(b, a), ndmin=2)
        # weight the model
        trace = lecture_traj * b_a.T
        # store trace in object
        if store is not None:
            self.store_trace(trace=trace, store_key=store)
        return trace

    def plot(self, keys, **kwargs):
        # wraps hypertools.plot for plotting multiple reconstructed traces
        # (see Experiment.plot for multisubject plotting)
        traces_toplot = [self.traces[k] for k in keys]
        return hyp.plot(traces_toplot, **kwargs)

    @property
    def all_questions(self, questions_path='../../data/raw/questions.tsv'):
        return pd.read_csv(questions_path,
                           sep='\t',
                           names=['index', 'video', 'question',
                                  'A', 'B', 'C', 'D'],
                           index_col='index')

    def _grade(self):
        # grades raw data to set self.data
        data = []
        question_blocks = (3, 8, 13)
        all_qs = self.all_questions
        for set_num, qblock in enumerate(question_blocks):
            question_block = self.raw_data['data'][qblock]['trialdata']
            answer_block = literal_eval(self.raw_data['data'][qblock + 1]['trialdata']['responses'])
            for q_num, q in enumerate(question_block):
                # deal with HTML characters
                q_text = unescape(q['prompt']).replace(chr(8217), "'")
                # match question text to question in dataset
                q_info = all_qs.loc[all_qs.question == q_text]
                # error on failure to match questions
                if not q_info.values.any():
                    raise KeyError(f"failed to find question matching {q_text}")
                # set qID and reference lecture
                qid = q_info.index[0]
                lec = q_info.loc[qid, 'video']
                # get answer
                ans_text = unescape(answer_block[f'Q{q_num}']).replace(chr(8217), "'")
                # error on failure to match question or unexpected letter
                try:
                    ans_let = q_info.squeeze()[q_info.squeeze() == ans_text].index[0]
                except IndexError as e:
                    raise KeyError(f"failed to find answer matching {ans_text}") from e
                assert ans_let in 'ABCD', f"found answer code {ans_let}, expected one of: 'A', 'B', 'C', 'D'"
                # set accuracy for response
                acc = 1 if ans_let == 'A' else 0
                data.append([qid, acc, set_num, lec])
        return pd.DataFrame(data, columns=['qID', 'accuracy', 'qset', 'lecture'])
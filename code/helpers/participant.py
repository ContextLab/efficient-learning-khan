import numpy as np
import pandas as pd
from ast import literal_eval
from html import unescape
from os.path import isfile, join as opj
from scipy.spatial.distance import cdist
from scipy.stats import entropy
from experiment import PARTICIPANTS_DIR, RAWDIR


# symmetrized KL divergence
# passed to scipy.spatial.distance.cdist in reconstruct_trace
def symmetric_kl(a, b, c=1e-11):
    return np.divide(entropy(a + c, b + c) + entropy(b + c, a + c), 2)


class Participant:
    def __init__(self, subid, data=None, raw_data=None, date_collected=None):
        self.subID = subid
        self.data = data
        _fallback_msg = "Attribute only set for participant created from raw " \
                       "PsiTurk data"
        if raw_data is None:
            self.raw_data = _fallback_msg
        else:
            self.raw_data = raw_data
        if date_collected is None:
            self.date_collected = _fallback_msg
        else:
            self.date_collected = date_collected
        self.traces = {}
        self.maps = {}

    @classmethod
    def from_psiturk(cls, psiturk_data, subid):
        raw_data = literal_eval(psiturk_data['datastring'])
        date_collected = psiturk_data['beginhit'].split()[0]
        p = cls(subid=subid, raw_data=raw_data, date_collected=date_collected)
        p.data = p._grade()
        return p

    @property
    def all_questions(self, questions_path=None):
        if questions_path is None:
            questions_path = opj(RAWDIR, 'questions.tsv')
        return pd.read_csv(questions_path,
                           sep='\t',
                           names=['index', 'video', 'question',
                                  'A', 'B', 'C', 'D'],
                           index_col='index')

    def __str__(self):
        return self.subID

    def __eq__(self, other):
        return self.subID == other

    def _grade(self):
        # grades raw data to set self.data
        data = []
        question_blocks = (3, 8, 13)
        all_qs = self.all_questions
        for set_num, qblock in enumerate(question_blocks):
            question_block = self.raw_data['data'][qblock]['trialdata']
            answer_block = literal_eval(
                self.raw_data['data'][qblock + 1]['trialdata']['responses']
            )
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
                    raise KeyError(
                        f"failed to find answer matching {ans_text}"
                    ) from e
                assert ans_let in 'ABCD', f"found answer code {ans_let}, " \
                                          f"expected one of: 'A', 'B', 'C', 'D'"
                # set accuracy for response
                acc = 1 if ans_let == 'A' else 0
                data.append([qid, acc, set_num, lec])
        return pd.DataFrame(data, columns=['qID', 'accuracy', 'qset', 'lecture'])

    def _repr_html_(self):
        # for displaying in Jupyter (IPython) notebooks
        print(self.__str__())
        try:
            return self.data.to_html()
        except AttributeError:
            return "Individual data unavailable"

    def head(self, *args, **kwargs):
        print(self.__str__())
        return self.data.head(*args, **kwargs)

    def get_data(self, qset=None, lecture=None):
        # return (a subset of) the subject's data
        if self.data is None:
            return f"No data for participant: {self.subID}"
        
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

    def get_trace(self, trace_key):
        """
        Getter for self.traces
        :param trace_key: str
                The key for the trace to be returned
        :return: trace: np.ndarray
                The trace stored under the given `trace_key`
        """
        try:
            return self.traces[trace_key]
        except KeyError as e:
            raise KeyError(
                f"No trace stored for {self} under {trace_key}. "
                f"Stored traces are: {', '.join(self.traces.keys())}"
            ) from e

    def reconstruct_trace(
            self,
            exp,
            content=None,
            lecture=None,
            qset=None,
            store=None,
            recon_lec=None
    ):
        """
        Reconstructs a participant's knowledge trace based on a lecture's
        trajectory, a set of questions' topic vectors, and binary accuracy scores
        :param exp: Experiment object
                Used to access lecture trajectory and question topic vectors
        :param content: numpy.ndarray
                The content against which to weight knowledge, as derived by
                question accuracy
        :param lecture: str, int, or iterable of strs/ints
                The lecture(s) for which to get questions and scores. If
                [default] None, get questions and scores for both lectures
                (& general knowledge)
        :param qset: int or iterable of ints
                The question set for which to get questions and scores. If
                [default] None, get data for all question sets
        :param store: str or None
                The key under which the reconstructed trace should be stored in
                self.traces. If [default] None, don't store the trace
        :param recon_lec: int or str
                The lecture trajectory to use in reconstructing the trace (if
                not passed directly via content). Useful if passing an iterable
                to lecture in order to get questions related to multiple lectures
        :return trace: numpy.ndarray
                The reconstructed trace, describing "knowledge" for each
                timepoint of given content.
        """
        data = self.get_data(qset=qset, lecture=lecture)
        acc = data['accuracy'].astype(bool)
        qids = data['qID'].tolist()
        question_vecs = exp.get_question_vecs(qids=qids)
        if content is None:
            if isinstance(lecture, (int, str)):
                content = exp.get_lecture_traj(lecture)
            elif hasattr(lecture, '__iter__'):
                if recon_lec is not None:
                    content = exp.get_lecture_traj(recon_lec)
                else:
                    raise ValueError("Must specify `content` or `recon_lec` if "
                                     "passing multiple `lecture`s")
            else:
                raise ValueError(
                    "lecture should be one of: str, int, iterable of str/int"
                )
        # compute timepoints by questions weights matrix
        wz = 1 - cdist(content, question_vecs, metric=symmetric_kl)
        # normalize
        wz -= wz.min()
        wz /= wz.max()
        # sum over questions (total possible weights for each timepoint)
        a = wz.sum(axis=1)
        # sum weights from correctly answered questions at each timepoint
        b = wz[:, acc].sum(axis=1)
        # divide weight from correct answers by total weight
        trace = b / a
        # store trace in object
        if store is not None:
            self.store_trace(trace=trace, store_key=store)
        return trace

    def save(self, filepath=None, allow_overwrite=False):
        if filepath is None:
            filepath = opj(PARTICIPANTS_DIR, f'{self.subID}.npy')
        if not allow_overwrite and isfile(filepath):
            print(f"{self.subID} not saved because {filepath} already exists. "
                  "Set allow_overwrite to True to replace the existing file")
        else:
            np.save(filepath, self)

    def store_trace(self, trace, store_key):
        self.traces[store_key] = trace

    # def plot(self, keys, **kwargs):
    #     # wraps hypertools.plot for plotting multiple reconstructed traces
    #     # (see Experiment.plot for multisubject plotting)
    #     if isinstance(keys, str):
    #         keys = [keys]
    #     traces_toplot = [self.traces[k] for k in keys]
    #     return hyp.plot(traces_toplot, **kwargs)

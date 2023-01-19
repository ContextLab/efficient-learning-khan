import pickle
from ast import literal_eval
from html import unescape
from pathlib import Path

import pandas as pd

from .constants import PARTICIPANTS_DIR, RAW_DIR


class Participant:
    def __init__(self, subid, data=None, raw_data=None, date_collected=None):
        self.subID = subid
        self.data = data
        _fallback_msg = ("Attribute only set for participant created from raw "
                         "PsiTurk data")
        if raw_data is None:
            self.raw_data = _fallback_msg
        else:
            self.raw_data = raw_data
        if date_collected is None:
            self.date_collected = _fallback_msg
        else:
            self.date_collected = date_collected
        self.traces = {}
        self.knowledge_maps = {}

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
            questions_path = RAW_DIR.joinpath('questions.tsv')
        return pd.read_csv(questions_path,
                           sep='\t',
                           names=['index', 'video', 'question',
                                  'A', 'B', 'C', 'D'],
                           index_col='index')

    def __repr__(self):
        output = f'Participant(subid="{self}"'
        if self.subID != 'avg':
            output = f'{output}, date_collected="{self.date_collected}"'
        return f'{output})'

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
                data.append([qid, acc, ans_let, set_num, lec])
        return pd.DataFrame(data, columns=['qID', 'accuracy', 'response', 'quiz', 'lecture'])

    def _repr_html_(self):
        # for displaying in Jupyter (IPython) notebooks
        print(repr(self))
        try:
            return self.data.to_html()
        except AttributeError:
            return "Individual data unavailable"

    def head(self, *args, **kwargs):
        return self.data.head(*args, **kwargs)

    def get_data(self, lecture=None, quiz=None):
        # return (a subset of) the subject's data
        if self.data is None:
            return f"No data for participant: {self.subID}"

        lec_keys = {'general': 0, 'forces': 1, 'bos': 2}
        if isinstance(quiz, int):
            quiz = [quiz]
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
        if quiz is not None:
            d = d.loc[d['quiz'].isin(quiz)]
        if lecture is not None:
            d = d.loc[d['lecture'].isin(lecture)]
        return d

    def get_kmap(self, kmap_key):
        """
        dict.get()-like access to self.knowledge_maps
        :param trace_key: str
                The key for the trace to be returned
        :return: trace: np.ndarray
                The trace stored under the given `trace_key`
        """
        try:
            return self.knowledge_maps[kmap_key]
        except KeyError as e:
            raise KeyError(
                f'No knowledge map stored for {self} under "{kmap_key}". Stored '
                f"knowledge maps are: {', '.join(self.knowledge_maps.keys())}"
            ) from e

    def get_trace(self, trace_key):
        """
        dict.get()-like access to self.traces
        :param trace_key: str
                The key for the trace to be returned
        :return: trace: np.ndarray
                The trace stored under the given `trace_key`
        """
        try:
            return self.traces[trace_key]
        except KeyError as e:
            raise KeyError(
                f"No trace stored for {self} under {trace_key}. Stored traces "
                f"are: {', '.join(self.traces.keys())}"
            ) from e

    def save(self, filepath=None, allow_overwrite=False):
        if filepath is None:
            filepath = PARTICIPANTS_DIR.joinpath(f'{self.subID}.p')
        else:
            filepath = Path(filepath)
        if not allow_overwrite and filepath.is_file():
            print(f"{self.subID} not saved because {filepath} already exists. "
                  "Set allow_overwrite to True to replace the existing file")
        else:
            filepath.write_bytes(pickle.dumps(self))

    def store_kmap(self, kmap, store_key):
        self.knowledge_maps[store_key] = kmap

    def store_trace(self, trace, store_key):
        self.traces[store_key] = trace

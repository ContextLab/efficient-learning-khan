from ast import literal_eval
from html import unescape
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist

from .constants import PARTICIPANTS_DIR, RAW_DIR
from .functions import rbf_sum


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
        return pd.DataFrame(data, columns=['qID', 'accuracy', 'response', 'qset', 'lecture'])

    def _repr_html_(self):
        # for displaying in Jupyter (IPython) notebooks
        print(self.__str__())
        try:
            return self.data.to_html()
        except AttributeError:
            return "Individual data unavailable"

    def head(self, *args, **kwargs):
        return self.data.head(*args, **kwargs)

    def get_data(self, lecture=None, qset=None):
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
        wz = 1 - cdist(content, question_vecs, metric='correlation')
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

    def construct_knowledge_map(self,
                                exp,
                                lecture,
                                qset,
                                map_grid,
                                rbf_width,
                                rbf_metric='euclidean',
                                store=None):
        assert isinstance(qset, int), "Must select data from a single question set"
        lec_keys = {1: 'forces', 2: 'bos'}

        # coerce lecture arg type
        if hasattr(lecture, '__iter__') and not isinstance(lecture, str):
            # should always be in this order for consistency
            assert len(lecture) == 2 and lecture[0] in ('forces', 1) and lecture[1] in ('bos', 2)
            lecture = list(lecture)
        else:
            if isinstance(lecture, int):
                lecture = lec_keys[lecture]
            lecture = [lecture]

        map_vertices = map_grid.reshape(map_grid.shape[0] * map_grid.shape[1], 2)
        qset_data = self.get_data(lecture=lecture, qset=qset)
        qids_seen = qset_data['qID']
        qids_correct = qset_data.loc[qset_data['accuracy'] == 1, 'qID']
        qembs_seen = exp.question_embeddings[qids_seen - 1]
        qembs_correct = exp.question_embeddings[qids_correct - 1]

        # raw_map = rbf(obs_coords=qembs_correct,
        #               pred_coords=map_vertices,
        #               width=rbf_width,
        #               metric=rbf_metric).sum(axis=0)
        # # no correct answers results in raw map of all 0's
        # if ~np.all(raw_map == 0):
        #     raw_map /= raw_map.max()
        # # normalize knowledge map by max possible knowledge given questions seen
        # weights_map = rbf(obs_coords=qembs_seen,
        #                   pred_coords=map_vertices,
        #                   width=rbf_width,
        #                   metric=rbf_metric).sum(axis=0)
        # weights_map /= weights_map.max()

        # normalize knowledge map by max possible knowledge given questions seen
        _weights_map = rbf_sum(obs_coords=qembs_seen,
                               pred_coords=map_vertices,
                               width=rbf_width,
                               metric=rbf_metric)
        weights_map = _weights_map / _weights_map.max()

        raw_map = rbf_sum(obs_coords=qembs_correct,
                          pred_coords=map_vertices,
                          width=rbf_width,
                          metric=rbf_metric)
        raw_map /= _weights_map.max()


        knowledge_map = (raw_map / weights_map).reshape(map_grid.shape[:2])
        if store is not None:
            self.store_kmap(knowledge_map, store_key=store)

        return knowledge_map

    def construct_learning_map(self,
                               qset_before,
                               qset_after,
                               lecture,
                               rbf_width,
                               rbf_metric='euclidean',
                               store=None):
        assert isinstance(qset_before, int) and isinstance(qset_after, int)
        if hasattr(lecture, '__iter__') and not isinstance(lecture, str):
            # should always be in this order for consistency
            assert len(lecture) == 2 and lecture[0] in ('forces', 1) and lecture[1] in ('bos', 2)
            kmap_key = 'forces_bos'
        elif lecture in ('forces', 1):
            kmap_key = 'forces'
        elif lecture in ('bos', 2):
            kmap_key = 'bos'
        else:
            raise ValueError('`lecture` may be either "forces" (or 1), "bos" '
                             '(or 2), or an iterable containing both')

        kmap_before = self.get_kmap(f'{kmap_key}_qset{qset_before}')
        kmap_after = self.get_kmap(f'{kmap_key}_qset{qset_after}')




    def save(self, filepath=None, allow_overwrite=False):
        if filepath is None:
            filepath = PARTICIPANTS_DIR.joinpath(f'{self.subID}.npy')
        if not allow_overwrite and Path(filepath).is_file():
            print(f"{self.subID} not saved because {filepath} already exists. "
                  "Set allow_overwrite to True to replace the existing file")
        else:
            np.save(filepath, self)

    def store_kmap(self, kmap, store_key):
        self.knowledge_maps[store_key] = kmap

    def store_trace(self, trace, store_key):
        self.traces[store_key] = trace

    # def plot(self, keys, **kwargs):
    #     # wraps hypertools.plot for plotting multiple reconstructed traces
    #     # (see Experiment.plot for multisubject plotting)
    #     if isinstance(keys, str):
    #         keys = [keys]
    #     traces_toplot = [self.traces[k] for k in keys]
    #     return hyp.plot(traces_toplot, **kwargs)

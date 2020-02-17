from ast import literal_eval
from os.path import join as opj

questions_path = '../../data/raw/questions.tsv'


class Participant:
    def __init__(self, subID, psiturk_data):
        self.subID = subID
        self.raw_data = literal_eval(psiturk_data)
        self.data = None    # set in self.grade

    def grade(self):
        # grades raw data and sets self.data
        pass

    def get_data(self, qset=None, lecture=None):
        question_blocks = (3, 8, 13)

        pass

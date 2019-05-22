from __future__ import division
import pandas as pd
from string import digits
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.stats import entropy
from collections import OrderedDict
import seaborn as sns
import matplotlib.pyplot as plt
import hypertools as hyp
import scipy
import numpy as np
import os


def model_topics(questions,videos,corpus=None,lda_params=None,vec_params=None):
    """
    Function that fits topic models to video content and uses it to transform video and question content
    
    Input:
        questions - 
        
        videos - 
        
        corpus - 
        
        lda_params - 
        
        vec_params - 
        
    Output:
    """
    
    
    
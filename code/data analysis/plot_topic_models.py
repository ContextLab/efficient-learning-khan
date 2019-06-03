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

def plot_topic_models(video_topics,question_topics,plot=True,savepath=None):
    """
    Function that plots topic models of video and question content
    
    Input:
        questions - 
        
        videos - 
        
    Output:
        video_topics - topic model for the video
        
        questions_topics - topic model for the questions
    """
    print("Modeling Topics!")
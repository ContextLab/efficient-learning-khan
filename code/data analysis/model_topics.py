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


def model_topics(v_windows,q_windows,corpus=None,lda_params=None,vec_params=None):
    """
    Function that fits topic models to video content and uses it to transform video and question content
    
    Input:
        questions - 
        
        videos - 
        
        corpus - 
        
        lda_params - 
        
        vec_params - 
        
    Output:
        video_topics - topic model for the video
        
        questions_topics - topic model for the questions
    """
    print("Running model")
    corpus = v_windows+q_windows
    # initialize count vectorizer
    tf_vectorizer = CountVectorizer(**vec_params)
    # fit the model
    tf_vectorizer.fit(v_windows+q_windows)

    # transform video windows
    video_tf = tf_vectorizer.transform(v_windows)

    # transform question samples
    questions_tf = tf_vectorizer.transform(q_windows)

    both_tf = tf_vectorizer.transform(v_windows+q_windows)

    # initialize topic model
    lda = LatentDirichletAllocation(**lda_params)

    # fit the topic model
    lda.fit(both_tf)

    # transform video topics
    video_topics = lda.transform(video_tf)

    # smooth model
    video_topics = pd.DataFrame(video_topics).rolling(25).mean().loc[25:,:].as_matrix()

    # transform question topics
    questions_topics = lda.transform(questions_tf)
    
    return video_topics, questions_topics


t1,t2 = model_topics(forces_video_samples,forces_questions_samples,lda_params=lda_params,vec_params=vec_params)

def model_lessons(v_windows, q_windows, vec_params, lda_params):
    """
    Function that fits a topic model to video content and uses it to transform video and question content
    """
    
    # initialize count vectorizer
    tf_vectorizer = CountVectorizer(**vec_params)
    # fit the model
    tf_vectorizer.fit(v_windows+q_windows)

    # transform video windows
    video_tf = tf_vectorizer.transform(v_windows)

    # transform question samples
    questions_tf = tf_vectorizer.transform(q_windows)

    both_tf = tf_vectorizer.transform(v_windows+q_windows)

    # initialize topic model
    lda = LatentDirichletAllocation(**lda_params)

    # fit the topic model
    lda.fit(both_tf)

    # transform video topics
    video_topics = lda.transform(video_tf)

    # smooth model
    video_topics = pd.DataFrame(video_topics).rolling(25).mean().loc[25:,:].as_matrix()

    # transform question topics
    questions_topics = lda.transform(questions_tf)
    
    return video_topics, questions_topics
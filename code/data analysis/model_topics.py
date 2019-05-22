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


def model_topics(videos,questions,corpus=None,lda_params=None,vec_params=None):
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
    print("Modeling Topics!")
    
    # create corpus from questions and videos if none provided
    if corpus is None:
        corpus = videos+questions
        
    # assign vectorizer and lda parameters if none provided
    if vec_params is None:
        vec_params = {
            'max_df': 0.95,
            'min_df': 2,
            'max_features': 500,
            'stop_words': 'english'
        }
    if lda_params is None: 
        lda_params = {
            'n_topics': 20,
            'max_iter': 10,
            'learning_method': 'online',
            'learning_offset':50.,
            'random_state': 0
        }
    
    # initialize count vectorizer
    tf_vectorizer = CountVectorizer(**vec_params)
    # fit the model
    tf_vectorizer.fit(videos+questions)

    # transform video windows
    video_tf = tf_vectorizer.transform(videos)

    # transform question samples
    questions_tf = tf_vectorizer.transform(questions)

    corpus_tf = tf_vectorizer.transform(videos+questions)

    # initialize topic model
    lda = LatentDirichletAllocation(**lda_params)

    # fit the topic model
    lda.fit(corpus_tf)

    # transform video topics
    video_topics = lda.transform(video_tf)

    # smooth model
    video_topics = pd.DataFrame(video_topics).rolling(25).mean().loc[25:,:].as_matrix()

    # transform question topics
    questions_topics = lda.transform(questions_tf)
    
    return video_topics, questions_topics


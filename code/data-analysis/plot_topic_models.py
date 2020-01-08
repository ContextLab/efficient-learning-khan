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
        
        plot - 
        
        savepath - 
        
    Output:
        video_topics - topic model for the video
        
        questions_topics - topic model for the questions
    """
    print("Plotting Topic Models!")
    
    # video topic proportions matrix
    sns.set_style('ticks')
    sns.set(font_scale=2)

    ax = sns.heatmap(pd.DataFrame(video_topics), yticklabels=False, xticklabels=False, vmin=0)#, cmap=sns.diverging_palette(300, 20, as_cmap=True))
    plt.xlabel('topics')
    plt.ylabel('time')
    plt.show()
    
    if savepath is not None:
        ax.get_figure().savefig(savepath + 'video_topic_props.pdf')

    # video model temporal structure
    ax = sns.heatmap(pd.DataFrame(video_topics).T.corr(), yticklabels=False, xticklabels=False, vmin=0)#, cmap=sns.diverging_palette(220, 20, as_cmap=True))
    plt.show()
    
    if savepath is not None:
        ax.get_figure().savefig(savepath + 'video_corr_matrix.pdf')

        
    # questions topic proportions matrix
    ax = sns.heatmap(pd.DataFrame(question_topics), yticklabels=False, xticklabels=False, vmin=0, linewidths=.001, linecolor='gray')# cmap=sns.diverging_palette(220, 20, as_cmap=True),
    plt.xlabel('topics')
    plt.ylabel('questions')
    plt.show()
    
    if savepath is not None:
        ax.get_figure().savefig(savepath + 'questions_topic_props.pdf')

    # questions model temporal structure
    ax = sns.heatmap(pd.DataFrame(question_topics).T.corr(), yticklabels=False, xticklabels=False, vmin=0)#, cmap=sns.diverging_palette(220, 20, as_cmap=True))
    plt.show()
    
    if savepath is not None:
        ax.get_figure().savefig(savepath + 'questions_corr_matrix.pdf')
        
    # 3D plot of video topic trajectory and question topics
    if savepath is None:
        _ = hyp.plot([pd.DataFrame(video_topics), pd.DataFrame(question_topics)], ['-','o'], azim=90)
    else:
        _ = hyp.plot([pd.DataFrame(video_topics), pd.DataFrame(question_topics)], ['-','o'], azim=90,
                    save_path = savepath + 'topic_trajectories.pdf')
        
        
        
    # correlations between topic vectors for each sliding window of video and each question
    sns.set_palette('hls')
    sns.set_style('white')
    plt.tight_layout()
    ax = plt.plot(1-scipy.spatial.distance.cdist(video_topics, question_topics, 'correlation'))
    plt.ylabel('correlation')
    plt.xlabel('time')
    plt.show()
    
    if savepath is not None:
        plt.savefig(savepath + 'dynamic_corr.pdf', bbox_inches='tight')
    


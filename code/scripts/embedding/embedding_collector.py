import os
import sys
import numpy as np
import pandas as pd
from os.path import isdir, join as opj
from shutil import copy2
from scipy.spatial.distance import pdist
from scipy.stats import pearsonr
from tqdm import tqdm
from embedding_config import config

order = sys.argv[1]


def spatial_similarity(emb, orig_pdist):
    # computes correlation between pairwise distances in embedding space and
    # pairwise distances in original space
    emb_pdist = pdist(np.vstack(emb), 'euclidean')
    return pearsonr(emb_pdist, orig_pdist)[0]


trajs_dir = opj(config['datadir'], 'trajectories')
embeddings_dir = opj(config['datadir'], 'embeddings')
results_dir = opj(config['datadir'], 'results')

if not isdir(results_dir):
    os.makedirs(opj(results_dir, 'embeddings'))
    os.makedirs(opj(results_dir, 'fit_reducers'))

# load video events in original topic space, pre-compute pairwise distance
forces_traj = np.load(opj(trajs_dir, 'forces_traj.npy'))
bos_traj = np.load(opj(trajs_dir, 'bos_traj.npy'))
questions_vecs = np.load(opj(trajs_dir, 'all_questions.npy'))
topic_space_pdist = pdist(np.vstack([forces_traj, bos_traj, questions_vecs]), 'correlation')

fpaths = []
corrs = []
print('collecting embeddings...')
pbar = tqdm(total=393900)
for order in range(1, 7):
    for seed in range(101):
        for nn in list(range(15, 200, 15)):
            for md in np.arange(.1, 1, .2):
                for sp in range(1, 11, 2):
                    for met in ['correlation', 'kl']:
                        fname = f"seed{seed}_nn{nn}_md{md}_sp{sp}_{met}.npy"
                        emb_path = opj(embeddings_dir, f'order{order}', fname)
                        emb_data = np.load(emb_path, allow_pickle=True)
                        corr = spatial_similarity(emb_data, topic_space_pdist)
                        corrs.append(corr)
                        fpaths.append(emb_path)
                        pbar.update(1)

np.save(opj(results_dir, 'corrs'), corrs)
np.save(opj(results_dir, 'fpaths'), fpaths)
best = fpaths[np.argsort(corrs)[-50:]]  # get 50 best
print("moving optimal results...")
for old_path in tqdm(best):
    new_fname = '_'.join(old_path.split('/')[-2:])
    new_path = opj(results_dir, 'embeddings', new_fname)
    old_model_path = old_path.replace('embeddings', 'fit_reducers')
    new_model_path = new_path.replace('embeddings', 'fit_reducers')
    copy2(old_path, new_path)
    copy2(old_model_path, new_model_path)
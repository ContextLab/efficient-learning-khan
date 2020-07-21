import sys
import numpy as np
from shutil import copy2
from scipy.spatial.distance import pdist
from scipy.stats import pearsonr
from embedding_config import config


def spatial_similarity(emb, orig_pdist):
    # computes correlation between pairwise distances in embedding space and
    # pairwise distances in original space
    emb_pdist = pdist(np.vstack(emb), 'euclidean')
    return pearsonr(emb_pdist, orig_pdist)[0]


seed = sys.argv[1]
trajs_dir = config['datadir'].joinpath('trajectories')
embeddings_dir = config['datadir'].joinpath('embeddings')
results_dir = config['datadir'].joinpath('results')
corrs_outfile = results_dir.joinpath(f'corrs_seed{seed}')
fpaths_outfile = results_dir.joinpath(f'fpaths_seed{seed}')

if corrs_outfile.is_file() and fpaths_outfile.is_file():
    sys.exit()

# load video events in original topic space, pre-compute pairwise distance
forces_traj = np.load(trajs_dir.joinpath('forces_lecture.npy'))
bos_traj = np.load(trajs_dir.joinpath('bos_lecture.npy'))
questions_vecs = np.load(trajs_dir.joinpath('all_questions.npy'))
topic_space_pdist = pdist(np.vstack([forces_traj, bos_traj, questions_vecs]), 'correlation')

fpaths = []
corrs = []
for order in range(1, 7):
    for nn in range(5, 31, 5):
        for md in (.1, .2, .3, .4, .5, .6, .7, .8, .9):
            for sp in range(1, 6):
                for met in ('euclidean', 'correlation'):
                    fname = f"seed{seed}_nn{nn}_md{md}_sp{sp}_{met}.npy"
                    emb_path = embeddings_dir.joinpath(f'order{order}', fname)
                    emb_data = np.load(emb_path, allow_pickle=True)
                    corr = spatial_similarity(emb_data, topic_space_pdist)
                    corrs.append(corr)
                    fpaths.append(emb_path)

np.save(corrs_outfile, corrs)
np.save(fpaths_outfile, fpaths)


################################################################################
# last collector script to finish compiles results
all_corrs = []
all_fpaths = []
print('loading files')
for seed in range(101):
    try:
        seed_corrs = np.load(results_dir.joinpath(f'corrs_seed{seed}.npy'))
        seed_fpaths = np.load(results_dir.joinpath(f'fpaths_seed{seed}.npy'))
        all_corrs.append(seed_corrs)
        all_fpaths.append(seed_fpaths)
    except FileNotFoundError:
        print(f"files for seed {seed} don't exist")
        sys.exit()

all_corrs = np.concatenate(all_corrs)
all_fpaths = np.concatenate(all_fpaths)
# get 50 best
best = all_fpaths[np.argsort(all_corrs)[-50:]]

# throw them all in a folder
print("moving optimal files")
results_dir.joinpath('optimized', 'embeddings').mkdir(parents=True)
results_dir.joinpath('optimized', 'fit_reducers').mkdir(parents=True)
for old_path in best:
    new_fname = '_'.join(old_path.split('/')[-2:])
    new_path = results_dir.joinpath('optimized', 'embeddings', new_fname)
    old_model_path = str(old_path).replace('embeddings', 'fit_reducers')
    new_model_path = str(new_path).replace('embeddings', 'fit_reducers')
    copy2(old_path, new_path)
    copy2(old_model_path, new_model_path)

import sys
import numpy as np
from umap import UMAP
from embedding_config import config
from embedding_helpers import correlation_exp


order, seed = int(sys.argv[1]), int(sys.argv[2])
trajs_dir = config['datadir'].joinpath('trajectories')
embeddings_dir = config['datadir'].joinpath('embeddings')
models_dir = config['datadir'].joinpath('fit_reducers')

ff_traj = np.load(trajs_dir.joinpath('forces_lecture.npy'))
bos_traj = np.load(trajs_dir.joinpath('bos_lecture.npy'))
questions = np.load(trajs_dir.joinpath('all_questions.npy'))

ff_len = len(ff_traj)
bos_len = len(bos_traj)

if order == 1:
    to_reduce = [ff_traj] + [bos_traj] + list(questions)
elif order == 2:
    to_reduce = [ff_traj] + list(questions) + [bos_traj]
elif order == 3:
    to_reduce = [bos_traj] + [ff_traj] + list(questions)
elif order == 4:
    to_reduce = [bos_traj] + list(questions) + [ff_traj]
elif order == 5:
    to_reduce = list(questions) + [ff_traj] + [bos_traj]
else:
    to_reduce = list(questions) + [bos_traj] + [ff_traj]

split_inds = np.cumsum([np.atleast_2d(vec).shape[0] for vec in to_reduce])[:-1]
stacked_vecs = np.log(np.vstack(to_reduce))

for n_neighbors in range(5, 31, 5):
    for min_dist in (.1, .2, .3, .4, .5, .6, .7, .8, .9):
        for spread in range(1, 6):
            fname = f"seed{seed}_nn{n_neighbors}_md{min_dist}_sp{spread}.npy"
            embpath = embeddings_dir.joinpath(f'order{order}', fname)
            modpath = models_dir.joinpath(f'order{order}', fname)
            if embpath.is_file() and modpath.is_file():
                continue

            params = {
                'n_components': 2,
                'init': 'spectral',
                'metric': correlation_exp,
                'random_state': seed,
                'n_neighbors': n_neighbors,
                'min_dist': min_dist,
                'spread': spread
            }
            np.random.seed(seed)
            reducer = UMAP(**params).fit(stacked_vecs)

            stacked_embeddings = reducer.embedding_
            embeddings = np.vsplit(stacked_embeddings, split_inds)

            ff_emb = next(i for i in embeddings if len(i) == ff_len)
            bos_emb = next(i for i in embeddings if len(i) == bos_len)
            qs_embs = np.squeeze([i for i in embeddings if len(i) == 1])
            embs_ordered = [ff_emb, bos_emb, qs_embs]

            np.save(embpath, embs_ordered)
            np.save(modpath, reducer)

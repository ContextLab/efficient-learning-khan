#!/usr/bin/python

import os
from glob import glob
from os.path import join as opj
from subprocess import run
from time import sleep
from embedding_config import config

scriptdir = config['scriptdir']
embeddings_dir = opj(config['datadir'], 'embeddings')
models_dir = opj(config['datadir'], 'fit_reducers')

to_resubmit = []
for fname in os.listdir(scriptdir):
    order, seed = fname.split('_')[-2:]
    pattern = opj(order, f'seed{seed}_*')
    n_embeddings = len(glob(opj(embeddings_dir, pattern)))
    n_reducers = len(glob(opj(models_dir, pattern)))
    if n_embeddings < 650 or n_reducers < 650:
        to_resubmit.append(fname)

for i, fname in enumerate(to_resubmit):
    print(f'resubmitting {i + 1}/{len(to_resubmit)}: {fname}')
    run(['mksub', opj(scriptdir, fname)])
    sleep(5)

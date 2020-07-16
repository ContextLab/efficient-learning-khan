#!/usr/bin/env/python
from glob import glob
from os import listdir
from os.path import join as opj
from subprocess import run, DEVNULL
from sys import exit
from time import sleep
from tqdm import tqdm
from embedding_config import config

scriptdir = config['scriptdir']
workingdir = config['workingdir']
jobname = config['jobname']
embeddings_dir = opj(config['datadir'], 'embeddings')
models_dir = opj(config['datadir'], 'fit_reducers')

submitted = listdir(scriptdir)
stdout_files = glob(opj(workingdir, f"{jobname}.o*"))

successful = []
for file in tqdm(stdout_files, desc='reading files'):
    fpath = opj(workingdir, file)
    with open(fpath, 'r') as f:
        content = f.read()

    script_name = content.split('script name: ')[1].split('\n')[0]
    successful.append(script_name)

to_resubmit = [script for script in submitted if script not in successful]
print("\n".join(to_resubmit))

n_found = len(to_resubmit)
if n_found == 0:
    print('all jobs run successfully')
    exit()
else:
    print(f"found {n_found} failed jobs to resubmit")

while True:
    response = input("resubmit jobs?\n[y/n]\n")
    if response not in ('y', 'n'):
        print("enter 'y' or 'n'")
        continue

    confirmed = response == 'y'
    if confirmed:
        break
    else:
        exit()

print('resubmitting jobs')
pbar = tqdm(total=len(to_resubmit))
for job in to_resubmit:
    pbar.set_description(f"resubmitting {job}")
    run([f"mksub {opj(scriptdir, job)}"], shell=True, stdout=DEVNULL)
    sleep(3)
    pbar.update()
pbar.close()







# to_resubmit = []
# for fname in listdir(scriptdir):
#     order, seed = fname.split('_')[-2:]
#     pattern = opj(order, f'seed{seed}_*')
#     n_embeddings = len(glob(opj(embeddings_dir, pattern)))
#     n_reducers = len(glob(opj(models_dir, pattern)))
#     if n_embeddings < 650 or n_reducers < 650:
#         to_resubmit.append(fname)
#
# for i, fname in enumerate(to_resubmit):
#     print(f'resubmitting {i + 1}/{len(to_resubmit)}: {fname}')
#     run(['mksub', opj(scriptdir, fname)])

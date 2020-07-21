import os
import time
from os import listdir
from os.path import join as opj
from embedding_config import config

BAR_LENGTH = 80

embeddings_dir = config['datadir'].joinpath('embeddings')
models_dir = config['datadir'].joinpath('fit_reducers')

orders = [f'order{o}' for o in range(1, 7)]
done = []
last_output = []

while len(done) < len(orders):
    prog_dict = {}
    progress = "progress:\n"
    for order in orders:
        if order in done:
            continue

        # n_done = len([i for i in os.listdir(data_dir) if os.stat(opj(data_dir, i)).st_mtime > 1575410400])
        n_done_embs = len(listdir(opj(embeddings_dir, order)))
        n_done_mods = len(listdir(opj(models_dir, order)))
        n_done = n_done_embs + n_done_mods
        pct_done = n_done / 131300
        if pct_done < 1:
            pct_todo = 1 - pct_done
            n_hashes = int(pct_done * BAR_LENGTH)
            key = order
            pct_prog = f'{str(pct_done * 100)[:5]}%'
            key_pad = ' ' * (10 - (len(key) + len(pct_prog))) + pct_prog + ' |'
            prog_info = key_pad + '#' * n_hashes + ' ' * (BAR_LENGTH - n_hashes) + '|'
            prog_dict[key] = prog_info
        else:
            done.append(order)
            continue

    output = []
    for k, v in sorted(prog_dict.items()):
        output.append(f'{k}\t{v}')
    if output != last_output:
        prog_made = 'Progress made!\n'
        # prog_made = '\n'
        # print(f'job finished at {time.strftime("%X", time.localtime())}')
    else:
        prog_made = '\n'
    last_output = output
    print('\n' * 49 + prog_made + '\n'.join(output))
    # time.sleep(120)

print('All jobs complete!')

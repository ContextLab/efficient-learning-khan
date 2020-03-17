#!/usr/bin/python

import os
from datetime import datetime as dt
from os.path import isdir, join as opj
from string import Template
from subprocess import run
from embedding_config import config as config


# ====== MODIFY ONLY THE CODE BETWEEN THESE LINES ======
job_script = opj(config['workingdir'], 'embedding_cruncher.py')
embeddings_dir = opj(config['datadir'], 'embeddings')
models_dir = opj(config['datadir'], 'fit_reducers')
min_seed = 0
max_seed = 100

job_commands = list()
job_names = list()

# order 1: forces, bos, questions
# order 2: forces, questions, bos
# order 3: bos, forces, questions
# order 4: bos, questions, forces
# order 5: questions, forces, bos
# order 6: questions, bos, forces

if not isdir(embeddings_dir):
    os.mkdir(embeddings_dir)
if not isdir(models_dir):
    os.mkdir(models_dir)

for order in range(1, 7):
    os.mkdir(opj(embeddings_dir, f'order{order}'))
    os.mkdir(opj(models_dir, f'order{order}'))

    for seed in range(min_seed, max_seed + 1):
        job_commands.append(f'{job_script} {order} {seed}')
        job_names.append(f'optimize_embedding_order{order}_{seed}')

# ====== MODIFY ONLY THE CODE BETWEEN THESE LINES ======

assert (len(job_commands) == len(job_names)), \
    "job_names and job_commands must have equal numbers of items"

# use largeq if more than 600 jobs are being submitted (Discovery policy)
if len(job_commands) > 600 and config['queue'] == 'default':
    config['queue'] = 'largeq'

# set command to activate conda env
if config['env_type'] == 'conda':
    config['activate_cmd'] = 'source activate'
    config['deactivate_cmd'] = 'conda deactivate'
else:
    raise ValueError("Only conda environments are currently supported")

JOBSCRIPT_TEMPLATE = Template(
"""#!/bin/bash -l
#PBS -N ${jobname}
#PBS -q ${queue}
#PBS -l nodes=${nnodes}:ppn=${ppn}
#PBS -l walltime=${walltime}

echo ---
script name: $job_name
echo loading modules: $modules
module load $modules

echo activating ${env_type} environment: $env_name
$activate_cmd $env_name

echo calling job script
$cmd_wrapper $job_command
echo job script finished
$deactivate_cmd
echo ---"""
)


class ScriptTemplate:
    def __init__(self, template, config):
        self.template = template
        self.config = config
        self.scriptdir = self.config['scriptdir']
        self.lockdir = self.config['lockdir']
        self.hostname = os.environ.get('HOSTNAME')
        self.username = os.environ.get('LOGNAME')
        self.locks = []

        # set submission command
        if self.username.startswith('f00'):
            self.submit_cmd = 'mksub'
        else:
            self.submit_cmd = 'qsub'

        # create directories if they don't already exist
        try:
            os.stat(self.scriptdir)
        except FileNotFoundError:
            os.mkdir(self.scriptdir)
        try:
            os.stat(self.lockdir)
        except FileNotFoundError:
            os.mkdir(self.lockdir)

    def lock(self, job_name):
        lockfile_path = opj(self.lockdir, f'{job_name}.LOCK')
        self.locks.append(lockfile_path)
        try:
            os.stat(lockfile_path)
            return True
        except FileNotFoundError:
            with open(lockfile_path, 'w') as f:
                f.writelines(f'LOCK CREATE TIME: {dt.now()} \n')
                f.writelines(f'HOST: {self.hostname} \n')
                f.writelines(f'USER: {self.username} \n')
                f.writelines('\n-----\nCONFIG\n-----\n')
                for opt, val in self.config.items():
                    f.writelines(f'{opt.upper()} : {val} \n')
            return False

    def release_locks(self):
        for l in self.locks:
            os.remove(l)
        os.rmdir(self.lockdir)

    def submit_job(self, jobscript_path):
        submission_cmd = f'echo "[SUBMITTING JOB: {jobscript_path}]"; {self.submit_cmd} {jobscript_path}'
        run([submission_cmd], shell=True)

    def write_scriptfile(self, job_name, job_command):
        filepath = opj(self.scriptdir, job_name)
        try:
            os.stat(filepath)
            return
        except FileNotFoundError:
            template_vals = self.config
            template_vals['job_name'] = job_name
            template_vals['job_command'] = job_command
            script_content = self.template.substitute(template_vals)
            with open(filepath, 'w+') as f:
                f.write(script_content)
            return filepath


script_template = ScriptTemplate(JOBSCRIPT_TEMPLATE, config)

for job_n, job_c in zip(job_names, job_commands):
    lockfile_exists = script_template.lock(job_n)
    if not lockfile_exists:
        script_filepath = script_template.write_scriptfile(job_n, job_c)
        if script_filepath:
            script_template.submit_job(script_filepath)

script_template.release_locks()

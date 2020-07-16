#!/usr/bin/python
from datetime import datetime as dt
import os
from string import Template
from subprocess import run, DEVNULL
from tqdm import tqdm
from embedding_config import config


# ====== MODIFY ONLY THE CODE BETWEEN THESE LINES ======
job_script = config['workingdir'].joinpath('embedding_collector.py')
results_dir = config['datadir'].joinpath('results')

min_seed = 0
max_seed = 100

job_commands = list()
job_names = list()

if not results_dir.is_dir():
    results_dir.mkdir()

for seed in range(min_seed, max_seed + 1):
    corrs_outfile = results_dir.joinpath(f'corrs_seed{seed}.npy')
    fpaths_outfile = results_dir.joinpath(f'fpaths_seed{seed}.npy')
    if not (corrs_outfile.is_file() and fpaths_outfile.is_file()):
        job_commands.append(f'{job_script} {seed}')
        job_names.append(f'embedding_collector_seed{seed}')

# overwrite for collector jobs
config['jobname'] = 'collector'
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
echo script name: $job_name
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
            self.scriptdir.stat()
        except FileNotFoundError:
            self.scriptdir.mkdir()
        try:
            self.lockdir.stat()
        except FileNotFoundError:
            self.lockdir.mkdir()

    def lock(self, job_name):
        lockfile_path = self.lockdir.joinpath(f'{job_name}.LOCK')
        self.locks.append(lockfile_path)
        try:
            lockfile_path.stat()
            return True
        except FileNotFoundError:
            with lockfile_path.open('w') as f:
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
        # submission_cmd = f'echo "[SUBMITTING JOB: {jobscript_path}]"; {self.submit_cmd} {jobscript_path}'
        submission_cmd = f'{self.submit_cmd} {jobscript_path}'
        run([submission_cmd], shell=True, stdout=DEVNULL)

    def write_scriptfile(self, job_name, job_command):
        filepath = self.scriptdir.joinpath(job_name)
        try:
            filepath.stat()
            return None
        except FileNotFoundError:
            template_vals = self.config
            template_vals['job_name'] = job_name
            template_vals['job_command'] = job_command
            script_content = self.template.substitute(template_vals)
            with filepath.open('w+') as f:
                f.write(script_content)
            return filepath


script_template = ScriptTemplate(JOBSCRIPT_TEMPLATE, config)

pbar = tqdm(total=len(job_names))
for job_n, job_c in zip(job_names, job_commands):
    pbar.set_description(f"submitting {job_n}")
    lockfile_exists = script_template.lock(job_n)
    if not lockfile_exists:
        script_filepath = script_template.write_scriptfile(job_n, job_c)
        if script_filepath:
            script_template.submit_job(script_filepath)

    pbar.update()

pbar.close()
script_template.release_locks()

# # quick progress bar & updates for job scripts' progress
# pbar = tqdm(total=202)
# while True:
#     n_done = len(os.listdir(results_dir))
#     if n_done < 202:
#         pbar.update(n_done - pbar.n)
#         sleep(1)
#     else:
#         pbar.close()
#         break
#
# print("compiling results...")

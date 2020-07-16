from pathlib import Path


config = dict()

# ====== MODIFY ONLY THE CODE BETWEEN THESE LINES ======
# job creation options
config['startdir'] = Path(__file__).resolve().parents[1]
config['workingdir'] = config['startdir'].joinpath('scripts')
config['datadir'] = config['startdir'].joinpath('data')
config['figdir'] = config['startdir'].joinpath('figures')
config['scriptdir'] = config['workingdir'].joinpath('scripts')
config['lockdir'] = config['workingdir'].joinpath('locks')

# runtime options
config['modules'] = 'python'
config['env_type'] = 'conda'
config['env_name'] = 'khan'
config['cmd_wrapper'] = 'python'
config['jobname'] = 'embedding'
config['queue'] = 'largeq'
config['nnodes'] = 1
config['ppn'] = 1
config['walltime'] = '18:00:00'
# ====== MODIFY ONLY THE CODE BETWEEN THESE LINES ======

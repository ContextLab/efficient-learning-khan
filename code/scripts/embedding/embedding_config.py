import socket
from os.path import dirname, realpath, join as opj

config = dict()

# ====== MODIFY ONLY THE CODE BETWEEN THESE LINES ======
# job creation options
config['startdir'] = opj(dirname(dirname(realpath(__file__))))
config['workingdir'] = opj(config['startdir'], 'scripts')
config['datadir'] = opj(config['startdir'], 'data')
config['figdir'] = opj(config['startdir'], 'figures')
config['scriptdir'] = opj(config['workingdir'], 'scripts')
config['lockdir'] = opj(config['workingdir'], 'locks')

# runtime options
config['modules'] = 'python'
config['env_type'] = 'conda'
config['env_name'] = 'khan'
config['cmd_wrapper'] = 'python'
config['jobname'] = 'embedding'
config['queue'] = 'largeq'
config['nnodes'] = 1
config['ppn'] = 1
config['walltime'] = '12:00:00'
# ====== MODIFY ONLY THE CODE BETWEEN THESE LINES ======

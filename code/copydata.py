# copies new data from docker to the local host and updates sql file

from subprocess import call, check_output

dockerdata = check_output('docker exec MD ls ../data', shell=True).strip().split('\n')
localdata = check_output('ls ../../data/', shell=True).strip().split('\n')

for folder in dockerdata:
    if folder not in localdata:
        call(['docker cp MD:../data/' + folder + ' ../../data/' + folder], shell=True)
        call(['echo copied ' + folder], shell=True)

call('echo Copying sql database', shell=True)

call('docker cp MD:config.txt ../../memorydynamics-1.1.db', shell=True)
call('echo Finished'), shell=True

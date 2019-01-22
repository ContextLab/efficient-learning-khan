////////////////////////////////////////////////////////////////////////////////
// INITIALIZE EXPERIMENT VARIABLES /////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

// collects custom ID and experimenter name if run in the lab
//mode = 'debug';
//mode = 'lab';
mode = 'mturk'

// Initalize psiturk object
var psiTurk = new PsiTurk(uniqueId, adServerLoc, mode);

//local testing and running:
//var serverport = '22364'; // should match psiturk config.txt file
//var serverporturl = 'http://localhost:'+serverport+'/'


//replace with static IP for online use!
//local debugging:
//var serverporturl = 'http://127.0.0.1/' //used in fitbit.html to open window

//online use:
var serverporturl = 'http://129.170.30.179/'

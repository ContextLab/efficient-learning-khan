# efficient-learning-khan

This repository contains code for the **Efficient Learning: Khan Academy** experiment, data analysis, and generated figures.


## Overview

Human knowledge is growing exponentially as new discoveries build upon one another, compounded by similarly accelerated advances in technology.  Nearly every student is familiar with the frustrations of typical classroom learning.  There is an ever-present mismatch between material he or she is struggling with the most and the material the instructor spends the most time teaching. This project constitutes the first step on the path to resolving such inefficiencies in individual learning. In this study, online participants answer three randomized sets of thirteen quiz question combining knowledge of general physics, the four forces of nature, and the birth of stars. Between these question blocks, participants view two (randomly ordered) Khan Academy lectures pertaining to the latter two topics. By modeling the dynamic content of the lecture videos, we are able reveal the information conveyed in each moment of the lesson. We then apply that model to the quiz questions to determine the knowledge tested by each, and map that knowledge onto a weighted combination of segments of lectures. With the modeled content of questions that participants answered correctly and incorrectly during each quiz block, we can estimate what knowledge and understanding they gained from the prior lesson, as well as predict what they will gain from the next lesson. Our method allows us to quantify successful acquisition of lecture knowledge via increasing similarity between the models of the lectures’ content and those of participants correctly answered questions, along with decreasing similarity between the lecture models and those of incorrectly answered questions. These models of and mappings of content learned, not learned, soon-to-be-learned, and previously known will allow us to build EEG data-based models for neural responses corresponding to each, allowing us to classify what a brain “looks like” when learning efficiently versus struggling. We aim to ultimately leverage these classifications into a deployable, low-cost hardware and software toolkit that will aid both instructors and students in real-world classroom environments.

## Running the experiment
The locally deployable version of the experiment may be run inside a Docker container as described here (for the MTURK-compatible version of the experiment, see the `mturk` branch).  A pre-configured image for the local experiment can be built from `Dockerfile-experiment`.  
0. Install Docker on your computer using the appropriate guide below:
- [OSX](https://docs.docker.com/docker-for-mac/install/#download-docker-for-mac)
- [Windows](https://docs.docker.com/docker-for-windows/install/)
- [Ubuntu](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)
- [Debian](https://docs.docker.com/engine/installation/linux/docker-ce/debian/)
1. Build the image from the `Dockerfile-experiment` file in this repository
 - `docker build -f Dockerfile-experiment -t khan-exp .`
2. Run a container from the image, exposing a port to run the experiment in a web browser
- `docker run -it -p 22363:22363 --name Khan-exp khan-exp`
3. You should now be inside the the container, in the `/psiturk/exp` directory. Start the PsiTurk shell and turn the server on
- `psiturk`
- `server on`
4. In a web browser, navigate to the port exposed to the container
- Open a browser window and enter `localhost:22363`
5. Once the experiment is finished running, shut down the server, exit the PsiTurk shell and exit the Docker container
- `server off`
- `exit`
- `exit`

**Note**: To run the container and experiment after the first time, skip steps 0-2 and instead start the existing container
- `docker start Khan-exp && docker attach Khan-exp`


## Running the analyses
A separate Docker container is available for reproducing and experimenting with the analyses performed in the paper. To create it:
0. Install Docker if you haven't already (see step 0 in **Running the experiment**)
1. Build the image from the `Dockerfile-analyses` file
- `docker build -f Dockerfile-analyses -t khan .`
2. Create a container based on the newly created image, exposing a port to run Jupyter Notebooks and bind-mounting the container to the repository's root directory to access the code and data files
- `docker run -it -p 22364:22364 --name Khan -v <PATH_TO_LOCAL_REPO>:/mnt khan`
3. You should now be inside the container, in the root directory (`/`). Navigate to the folder containing the analysis notebooks and.
- `cd /mnt/code/notebooks`
4. Start a local Jupyter Notebook server on the port exposed to your local machine, and suppress automatically opening a browser (since there isn't one in the container)
- `jupyter notebook --port=22364 --no-browser --ip=0.0.0.0 --allow-root`
5. Copy the **third** link that appears (the one starting with `http://127.0.0.1:22364`) and paste it into a web browser
6. The container pre-installs some nifty extensions for customizing the Jupyter Notebook interface.  If you want to enable any of them:
- click on the `Nbextensions` tab on the Jupyter server page in a browser
- uncheck the "disable configuration for nbextensions without explicit compatibility" box (don't worry, nearly all of them _are_ compatible, we're just using a newer version of `jupyter-notebook`)
- click on any of the listed extensions to see a description and further options, and check the box next to enable it
- refresh any running notebooks to apply the changes

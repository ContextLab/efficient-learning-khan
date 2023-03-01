# Text embedding models yield high-resolution insights into conceptual knowledge from short multiple-choice quizzes

<p align="center">
  <a href="https://psyarxiv.com/dh3q2">
    <img src="https://img.shields.io/badge/PsyArXiv-Preprint-cf1d35.svg" alt="PsiArXiv preprint">
  </a>
</p>

This repository contains all data and code used to produce the paper
"[_Text embedding models yield high-resolution insights into conceptual
knowledge from short multiple-choice quizzes_](https://psyarxiv.com/dh3q2)" by
Paxton C. Fitzpatrick, Andrew C. Heusser, and Jeremy R. Manning.

We also include reproducible environments for running our experiment and
analyses via [Docker](https://www.docker.com/).


## Table of Contents

- [Repo Organization](#repo-organization)
- [Installing Docker](#installing-docker)
- [Running the Analyses](#running-the-analyses)
  - [Option 1: `launch_notebooks.sh`](#option-1-launch_notebookssh)
  - [Option 2: Manual setup](#option-2-manual-setup)
  - [Additional info](#additional-info)
- [Running the Experiment](#running-the-experiment)
- [Useful docs](#useful-docs)


## Repo Organization

The repository is organized as follows:

```yaml
.
├── code : all analysis code used in the paper
│   ├─ notebooks : Jupyter notebooks for running analyses
│   └─── khan_helpers : Python package with helper code for analyses
├── data : all data analyzed in the paper
│   ├── embeddings : 2D UMAP embeddings for knowledge maps
│   ├── models : trained models
│   ├── participants : individual & average participant data objects
│   ├── raw : raw lecture transcripts, quiz questions, and performance data
│   └── trajectories : topic trajectories for lectures and question sets
├── docker : files for building experiment & analysis environments
├── exp : all code for running the experiment
│   ├── static : stimuli, scripts, stylesheets, and other static files
│   └── templates : HTML templates for experiment pages
└── paper : all files for generating the paper
    ├── CDL-bibliography : submodule for CDL BibTeX file
    ├── admin : files related to submission & review process
    └── figs : PDFs of all figures from the paper
```


## Installing Docker

You can install the [Docker Desktop](https://docs.docker.com/desktop/) app for
your operating system using one of the guides below:

- [MacOS](https://docs.docker.com/docker-for-mac/install/) (Intel or Apple Silicon)
- [Windows](https://docs.docker.com/docker-for-windows/install/)
- [Debian](https://docs.docker.com/desktop/install/debian/)
- [Fedora](https://docs.docker.com/desktop/install/fedora/)
- [Ubuntu](https://docs.docker.com/desktop/install/ubuntu/)
- [Arch](https://docs.docker.com/desktop/install/archlinux/)

Alternatively, you can install [Docker Engine](https://docs.docker.com/engine/)
(CLI only) for various Linux OSes using one of the guides listed
[here](https://docs.docker.com/engine/install/#server).

**You do not need to create a Docker ID or Docker Hub account to use Docker with
this repo.**


## Running the Analyses

### Option 1: [`launch_notebooks.sh`](launch_notebooks.sh)

The easiest way to set up and run the analyses is to use the
[`launch_notebooks.sh`](launch_notebooks.sh) script included in this repository.
From the repository root, simply run:

```sh
./launch_notebooks.sh
```

The script will:

1. Start the Docker daemon, if it isn't already running
2. Build the image from [`Dockerfile-analyses`](docker/Dockerfile-analyses), if
   it doesn't already exist
3. Create and run a container from the image, if one doesn't already exist
4. Launch a [Jupyter notebook](https://jupyter.org/) server inside the 
   container, if one isn't already running
5. Open the notebook app in your default browser
6. Attach stdout to the notebook server logs in the container

The script also accepts a few options to customize behavior:

```console
$ ./launch_notebooks.sh --help

launch_notebooks.sh [-h] [-d] [-b] [-i NAME] [-c NAME]

Launch a Jupyter notebook server inside a Docker container for running the
analysis notebooks. The container is set up automatically the first time the
script is run.

Options:
   -h, --help                   Show this help message and exit
   -d, --detach                 Don't attach the terminal to the streaming
                                notebook server log
   -b, --no-browser             Don't try to automatically open notebooks in a
                                browser window
   -i, --image-name NAME        Run a container from existing image NAME, or
                                build a new image and tag it NAME
   -c, --container-name NAME    Start the existing container NAME, or create a
                                new container named NAME
```

To stop the notebook server and exit the container, press **Control+c**.

The script should work on most systems. If for some reason it doesn't work for
you, or you prefer to manage the environment manually, you can build and run the
analysis environment following the steps below
(and if you encounter any errors, feel free to
[open an issue](https://github.com/ContextLab/efficient-learning-khan/issues/new)!).

### Option 2: Manual setup

1. After [installing Docker](#installing-docker), launch the desktop app or 
   start the daemon from the command line.
2. _From the repository's root directory_, build the "`khan`" image from the 
   [Dockerfile-analyses](docker/Dockerfile-analyses) file in the 
   [docker](docker) directory:

   ```sh
   docker build --rm -f docker/Dockerfile-analyses -t khan .
   ```

3. Run a container (named "`Khan`") from the newly built image:

   ```sh
   docker run -it -p 8888:8888 --name Khan -v $PWD:/mnt khan
   ```

   The command above binds port 8888 in the continer to port 8888 on the host so 
   we can access the Jupyter notebook server from a web browser, and bind-mounts 
   the repository to the container's `/mnt` directory so we can read and write 
   files from inside it.

4. The notebook server will launch automatically when the container is run. Copy 
   and paste the 3rd link that appears (the one starting with 
   `http://127.0.0.1:8888`) into a web browser to access the notebook app.

5. You can then open any notebook in [`code/notebooks/`](code/notebooks) and 
   run the code inside it. When finished, return to the terminal and press 
   **Control+c** to stop the notebook server and exit the container.

6. To launch the container and notebooks any time after this initial setup, run:

   ```sh
   docker start Khan && docker attach Khan
   ```


### Additional information

- You can launch an interactive `bash` shell inside the container to explore or 
  modify its contents with `docker exec -it Khan bash`. To exit the container, 
  either press **Control+d** or type `exit`. **Note** that:
  - if the container isn't already running, you must start it first with 
    `docker start Khan`
  - When you enter the container this way (rather than with `docker attach` or 
    the [`launch_notebooks.sh`](launch_notebooks.sh) script), the container 
    isn't automatically stopped when you exit it. To stop the container after 
    exiting, use `docker stop Khan`
- You can get the URL of the running notebook server from inside the container 
  with `jupyter notebook list`
- The container pre-installs some nifty 
  [extensions](https://jupyter-contrib-nbextensions.readthedocs.io/en/latest/index.html) 
  for customizing the Jupyter Notebook interface. If you want to enable any of 
  them:
  - Open the notebook application in a browser and click on the "**Nbextensions**" tab.  (To
    launch the notebook application, start the notebook server as described above and visit
    the server's address in your web browser.)
  - Uncheck the "_disable configuration for nbextensions without explicit 
    compatibility ..._" box (nearly all of them _are_ compatible, we're just 
    using a newer version of Jupyter notebooks).
  - Click on any of the listed extensions to see a description and further 
    options, and check the box next to its name to enable it.
  - Refresh any running notebooks for changes to take effect.


## Running the Experiment

1. After [installing Docker](#installing-docker), launch the desktop app or 
   start the daemon from the command line.
2. _From the repository's root directory_, build the "`khan-exp`" image from the 
   [Dockerfile-experiment](docker/Dockerfile-experiment) file in the 
   [docker](docker) directory:

   ```sh
   docker build --rm -f docker/Dockerfile-experiment -t khan-exp .
   ```

3. Run a container (named "`Khan-exp`") from the newly built image:

   ```sh
   docker run -it -p 22363:22363 -v "$PWD/exp:/exp" --name Khan-exp khan-exp
   ```

   The command above bind-mounts the container to the repository's [`exp/`](exp) 
   directory so the psiTurk server can read and run the experiment code, and 
   binds port 22363 between the container and host so the server can be accessed 
   from a web browser.

   **Note**: the port published by the container must match the port listed in 
   [`exp/config.txt`](exp/config.txt).

4. Your shell prompt (`$PS1`) should now start with `root@`, indicating that 
   you're now running a `bash` shell from _inside_ the container. To start the 
   psiTurk experiment server, run:

   ```sh
   psiturk server on
   ```

   When you see "_`Now serving on http://0.0.0.0:22363`_," the experiment server 
   is ready. Starting the server for the first time will also create 
   `exp/server.log`, a logfile for the experiment server, and 
   `exp/efficient-learning-khan.db`, a SQLite database to hold raw experiment 
   data.

5. Generate a link to the experiment in "debug mode":

   ```sh
   psiturk debug -p
   ```

   This will output a URL in the format 
   `http://0.0.0.0:22363/ad?assignmentId=debug<XXXXXX>&hitId=debug<YYYYYY>&workerId=debug<ZZZZZZ>&mode=debug`, 
   where `<XXXXXX>` and `<ZZZZZZ>` will form a unique identifier for the run 
   (i.e., a participant's unique ID). In debug mode, the experiment will behave 
   normally and data will still be saved properly, but psiTurk will not try to 
   connect to [Amazon Mechanical Turk](https://www.mturk.com/)'s servers. This 
   is useful because it enables the experiment to be run locally without the 
   user having to create AWS & MTurk accounts, supply access keys, etc.

6. Copy and paste the URL into a web browser, and follow the on-screen 
   instructions to progress through the experiment. **Note**: the experiment 
   will not work in Google Chrome. Recommended browsers include Safari and 
   Firefox.

7. When finished, return to the terminal and shut down the experiment server:

   ```sh
   psiturk server off
   ```

   and exit the Docker container by pressing **Control+d** or typing `exit`.

8. To start and enter the container any time after this initial setup, run:

   ```sh
   docker start Khan-exp && docker attach Khan-exp
   ```


## Useful additional documentation
- [Docker](https://docs.docker.com/)
  - [`Dockerfile` reference](https://docs.docker.com/engine/reference/builder/)
  - [`docker build` command reference](https://docs.docker.com/engine/reference/commandline/build/)
  - [`docker run` command reference](https://docs.docker.com/engine/reference/run/)
- [Jupyter notebook (v6.4.7)](https://jupyter-notebook.readthedocs.io/en/v6.4.7/)
- [psiTurk](https://psiturk.readthedocs.io/en/stable/)
  - [psiTurk shell commands](https://psiturk.readthedocs.io/en/stable/command_line.html)
  - [Guide to `config.txt` fields](https://psiturk.readthedocs.io/en/stable/settings.html)

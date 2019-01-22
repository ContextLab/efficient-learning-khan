# Dockerfile for psiturk container
FROM debian:stretch
MAINTAINER Max Bluestone <mbluestone93@gmail.edu>

# install debian-related stuff
RUN apt-get update
RUN apt-get install -y eatmydata
RUN eatmydata apt-get install -y \
    python-dev \
    default-libmysqlclient-dev \
    python-pip \
    procps \
    git \
    yasm
RUN rm -rf /var/lib/apt/lists/*

# install python packages
RUN pip install --upgrade pip
RUN pip install --upgrade \
setuptools \
requests \
mysql-python \
psiturk \
pydub \
matplotlib \
pandas \
numpy \
quail \
seaborn \
hypertools \
joblib \
sqlalchemy \
scipy \
deepdish \
datetime \
python-dateutil \
requests-oauthlib

# install vim
RUN apt-get update
RUN apt-get install -y vim

# add experiment and data folders
COPY exp /exp
COPY data /data
COPY code /code

# add stimuli folder
# COPY stimuli /exp/stimuli

# setup working directory
WORKDIR /exp

# set up psiturk to use the .psiturkconfig in /
ENV PSITURK_GLOBAL_CONFIG_LOCATION=/

# expose port to access psiturk from outside
EXPOSE 22363

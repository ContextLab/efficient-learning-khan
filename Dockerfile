# Dockerfile for psiturk container
FROM debian:stretch
MAINTAINER Paxton Fitzpatrick <paxton.c.fitzpatrick.19@dartmouth.edu>

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
psiturk==2.2.3 \
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
deepdish


# install ffmpeg
RUN git clone https://github.com/FFmpeg/FFmpeg
RUN cd FFmpeg && ./configure --enable-gpl && \
make && make install && ldconfig

RUN pip install \
git+https://github.com/ContextLab/psiTurk.git@expose-gunicorn-timeout-parameter

# install vim
RUN apt-get update
RUN apt-get install -y vim

# add experiment and data folders
COPY memory-dynamics/exp /exp
COPY memory-dynamics/data /data
COPY memory-dynamics/code /code

# add stimuli folder
# COPY video-stims /exp/video-stims

# setup working directory
WORKDIR /exp

# set up psiturk to use the .psiturkconfig in /
ENV PSITURK_GLOBAL_CONFIG_LOCATION=/

# expose port to access psiturk from outside
EXPOSE 22363

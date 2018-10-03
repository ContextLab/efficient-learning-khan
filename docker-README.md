# to run build the docker and run the experiment inside:
# place memory-dynamics repo, data dir, and video-stims dir in same enclosing dir

# to build and start for the first time:
#   with docker running:
#   from enclosing dir: `docker build -t memorydynamics:latest -f memory-dynamics/Dockerfile .`
#   from eclosing dir: `docker run -it -p 22363:22363 --mount type=bind,"source=$(pwd)/data",target=/data --name MD memorydynamics`

# to start subsequent times:
#   with docker running:
#   from enclosing dir: `docker start MD`
#   from enclosing dir: `docker exec -it MD bash`

# to run experiment:
#   start docker (see above)
#   `psiturk`
#   `server on`
#   open Google Chrome and go to `localhost:22363`

# to end experiment:
#   `server off`
#   `exit` exits psiturk
#   `exit` exits docker





# made a mistake?
#   to delete container and and start over: `docker rm MD`

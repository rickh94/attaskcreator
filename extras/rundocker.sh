#!/bin/sh
# args: name, configdir, logdir
docker run -d --name $1 -v $2:/config -v $3:/logs rickh94/attaskcreator:latest

#!/bin/bash

DIR=`pwd`

rsync -avz --delete --exclude 'build.sh' --exclude '.git' ${DIR} pi@192.168.137.195:/home/pi/

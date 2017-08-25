#!/usr/bin/env bash
source ./activate
if [ -f ./pid.txt ]; then
  echo "pidfile.txt exists!"
else
  nohup ./periodic.py >>log.txt 2>&1 &
  echo $! > pid.txt
  echo "successfully started!"
fi

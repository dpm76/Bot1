#!/bin/bash

if [ "$1" == "-h" ]  || [ "$1" == "--help" ]
then
  echo -e "Starts Bot1 listener."
  echo -e "\t--help -h \tShows this help message."
  echo -e "\t--init-motor -i \tInits PWM for motors (mandatory the first time of execution after boot)."
  exit 0
fi

if [ "$1" == "--init-motor" ] || [ "$1" == "-i" ]
then
  ./init-motor.sh
fi
export PYTHONPATH=./bot1
rpyc_classic.py


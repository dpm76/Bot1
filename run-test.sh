#!/bin/bash

if [ "$1" == "-h" ]  || [ "$1" == "--help" ]
then
  echo -e "Runs a playground test."
  echo -e ""
  echo -e "example:\t$0 path-to-test -i"
  echo -e "\t\t$0 -h"
  echo -e ""
  echo -e "--help \t\t-h \tShows this help message and exits."
  echo -e "--init-motor \t-i \tInits PWM for motors"
  echo -e "\t\t\tMandatory the first time of execution after boot. Then can be omitted"
  echo -e ""
  echo -e "Some tests must be run as root, so please use sudo."
  exit 0
fi

if [ "$2" == "--init-motor" ] || [ "$2" == "-i" ]
then
  ./init-motor.sh
fi

MY_PATH="$(realpath $0)"
MY_DIR="$(dirname $MY_PATH)"

export PYTHONPATH=$MY_DIR/bot1
python3 $1

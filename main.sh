#!/bin/bash

ADD() {
  source ./script/ADD.sh
}

CHECK() {
  ./script/CHECK.sh
}

CONFIG() {
  source ./script/CONFIG.sh
}

while true; do

  OP=$(dialog --title "Welcome to IMF" --menu "Select Option" 15 30 4 \
    1 "ADD & DEL Mikrotik" \
    2 "Check Mikrotik" \
    3 "Config Mikrotik" \
    4 "Exit" 3>&1 1>&2 2>&3)

  case $OP in
  1) ADD ;;
  2) CHECK ;;
  3) CONFIG ;;
  4) exit 0 ;;
  esac
done

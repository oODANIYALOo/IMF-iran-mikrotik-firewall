#!/bin/bash


MK_ADD() {
  ADRESS=$(dialog --form "$MSG" 10 50 4 \
    "IP: " 1 1 "$IP" 1 12 20 0 \
    "USER: " 2 1 "$USR" 2 12 20 0 \
    "PASSWORD: " 3 1 "$PASSWORD" 3 12 20 0 3>&1 1>&2 2>&3)
  CHECK
}
CHECK() {
  TEMP=$(echo $ADRESS | grep -o " " | wc -l)
  if [[ $TEMP != 2 ]]; then
    MSG="Please dont use space AND fill all box"
    MK_ADD
  fi

  IP=$(echo $ADRESS | cut -d " " -f1)
  USR=$(echo $ADRESS | cut -d " " -f2)
  PASSWORD=$(echo $ADRESS | cut -d " " -f3)

  if ! [[ "$IP" =~ ^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$ ]]; then
    MSG="IP incorrect"
    MK_ADD
  elif ! [[ "$USR" =~ ^[a-z,A-Z,0-9]{3,32}$ ]]; then
    MSG="USER incorrect"
    MK_ADD
  elif ! [[ $PASSWORD =~ ^[a-z,A-Z,0-9]{1,50}$ ]]; then
    MSG="PASSWORD incorrect"
    MK_ADD
  fi
}

ADD() {
	MSG="Enter Mikrotik Info"
	while true; do

  OP=$(dialog --title "Welcome to IMF" --menu "Select Option" 15 40 4 \
    1 "ADD SSH Mikrotik" \
    2 "DELELT SSH Mikrotik" \
    3 "SHOW all Mikrotik" \
    4 "back" 3>&1 1>&2 2>&3)

  	case $OP in
  		1) MK_ADD ;;
  		2) MK_DEL ;;
  		3) MK_SHOW ;;
  		4) return ;;
  		esac
	done


  ENTRY

  #dialog --title "massage" --msgbox "add successful :)" 6 35
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

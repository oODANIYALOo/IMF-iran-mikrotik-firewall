#!/bin/bash

MSG="Enter Mikrotik Info"
ENTRY() {
  ADRESS=$(dialog --form "$MSG" 10 45 4 \
    "IP: " 1 1 "$IP" 1 12 20 0 \
    "USER: " 2 1 "$USR" 2 12 20 0 \
    "PASSWORD: " 3 1 "$PASSWORD" 3 12 20 0 3>&1 1>&2 2>&3)
  CHECK
}

CHECK() {
  TEMP=$(echo $ADRESS | grep -o " " | wc -l)
  if [[ $TEMP != 2 ]]; then
    MSG="Please dont use space AND fill all box"
    ENTRY
  fi

  IP=$(echo $ADRESS | cut -d " " -f1)
  USR=$(echo $ADRESS | cut -d " " -f2)
  PASSWORD=$(echo $ADRESS | cut -d " " -f3)

  if ! [[ "$IP" =~ ^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$ ]]; then
    MSG="IP incorrect"
    ENTRY
  elif ! [[ "$USR" =~ ^[a-z,A-Z,0-9]{3,32}$ ]]; then
    MSG="USER incorrect"
    ENTRY
  elif ! [[ $PASSWORD =~ ^[a-z,A-Z,0-9]{1,50}$ ]]; then
    MSG="PASSWORD incorrect"
    ENTRY
  fi
}

ENTRY

# backup all inventory
date >>./ansible-run/.inventory.ini.log
cat ./ansible-run/inventory.ini >>./ansible-run/.inventory.ini.log

# create inventory.ini
sed -e "s/IIP/$IP/g" -e "s/UUSER/$USR/g" -e "s/PPASSWORD/$PASSWORD/g" ./ansible-run/.inventory.ini >./ansible-run/inventory.ini

dialog --title "massage" --msgbox "add successful :)" 6 26

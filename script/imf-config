#!/bin/bash

SET-HOSTNAME() {
  echo hostname
}

VLAN() {
  echo VLAN
}

DHCP-SERVER() {
  echo DHCP-SERVER
}

FIREWALL() {
  echo FIREWALL
}

SET-NTP() {
  echo SET-NTP
}

SIMPLE-HARDEN() {
  echo SIMPLE-HARDEN
}

ADD-ROUTE() {
  echo ADD-ROUTE
}

ANSWER=$(dialog --checklist "checklist" 20 35 18 \
  "SET-HOSTNAME" 1 "off" \
  "VLAN" 2 "off" \
  "DHCP-SERVER" 3 "off" \
  "FIREWALL" 4 "off" \
  "SET-NTP" 5 "off" \
  "SIMPLE-HARDEN" 6 "off" \
  "ADD-ROUTE" 7 "off" 3>&1 1>&2 2>&3)

for OP in $ANSWER; do
  case "$OP" in
  SET-HOSTNAME)
    SET-HOSTNAME
    ;;
  VLAN)
    VLAN
    ;;
  DHCP-SERVER)
    DHCP-SERVER
    ;;
  FIREWALL)
    FIREWALL
    ;;
  SET-NTP)
    SET-NTP
    ;;
  SIMPLE-HARDEN)
    SIMPLE-HARDEN
    ;;
  ADD-ROUTE)
    ADD-ROUTE
    ;;
  *)
    echo error case: wrong input $OP
    ;;
  esac

done

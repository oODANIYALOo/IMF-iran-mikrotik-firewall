#!/bin/bash

if ANSWER=$(ansible mikrotik -m community.routeros.command -a '{"commands": ["/system resource print"]}' -i ./ansible-run/inventory.ini); then
  dialog --title "output" --msgbox "$(printf "%s\n" "$ANSWER" | grep -e version -e memory -e cpu -e platform | tail -8 | cut -d "\"" -f 2)" 12 45
else
  dialog --title "error" --msgbox "host is down please check :(" 5 35
fi

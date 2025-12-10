#!/bin/bash


MK_ADD() {
	ADRESS=$(dialog --form "Enter your ssh mikrotik info" 10 50 4 \
		"IP: " 1 1 "" 1 12 20 0 \
		"USER: " 2 1 "" 2 12 20 0 \
		"PASSWORD: " 3 1 "" 3 12 20 0 3>&1 1>&2 2>&3)
	
	IP=$(echo $ADRESS | cut -d " " -f1)
	USR=$(echo $ADRESS | cut -d " " -f2)
	PASSWORD=$(echo $ADRESS | cut -d " " -f3)

	OUTPUT=$(imf-inventory add $IP $USR $PASSWORD)
	dialog --title "massage" --msgbox "$OUTPUT" 6 35
}

MK_DEL() {
	ADRESS=$(dialog --form "enter ip or number of mikrotik for delete" 10 60 4 \
		"IP or NUMBER: " 1 1 "" 1 20 20 0 3>&1 1>&2 2>&3)
	
	OUTPUT=$(imf-inventory del $ADRESS)
	dialog --title "massage" --msgbox "$OUTPUT" 6 35
	
}

MK_SHOW() {
	OUTPUT=$(imf-inventory show)
	dialog --title "massage" --msgbox "$OUTPUT" 15 50	
}

:'
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
':
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

  #dialog --title "massage" --msgbox "add successful :)" 6 35
}

CHECK() {
	if ANSWER=$(ansible allmikrotik -m community.routeros.command \
	       	-a '{"commands": ["/system resource print"]}' -i inventory.ini); then
  		dialog --title "output" --msgbox "$(printf "%s\n" "$ANSWER" | grep -e version -e memory -e cpu -e platform |\
		       	tail -8 | cut -d "\"" -f 2)" 12 45
	else
		dialog --title "error" --msgbox "host is down please check :(" 5 35
	fi
}

CONFIG() {
  source ./script/CONFIG.sh
}

WEB() {
	SEC=4
	(
		for i in {1..100}; do
			echo $i
			sleep $(echo "scale=2; $SEC/100" | bc)
  		done
	) | dialog --gauge "loading run web server..." 10 70 0 &
	DIALOG_PID=$!
	
	date >> web/runserver.log
	python web/manage.py runserver 2>> web/runserver.log 1>&2 &
	WEB_EXIT=$?

	sleep 4 && kill $DIALOG_PID 2>/dev/null
	wait $DIALOG_PID 2>/dev/null

	if [ $WEB_EXIT -eq 0 ]; then
		 dialog --title "successful Run" --msgbox "Web interface successful run in port 8000" 5 50 
	else
		 dialog --title "ERROR" --msgbox "plase check web/runserver.log" 5 50
	fi
}

while true; do

  OP=$(dialog --title "Welcome to IMF" --menu "Select Option" 15 30 5 \
    1 "ADD & DEL Mikrotik" \
    2 "Check Mikrotik" \
    3 "Config Mikrotik" \
    4 "Run web interface" \
    5 "Exit" 3>&1 1>&2 2>&3)

  case $OP in
  1) ADD ;;
  2) CHECK ;;
  3) CONFIG ;;
  4) WEB;;
  5) exit 0 ;;
  esac
done

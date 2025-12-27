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
	dialog --title "=== Mikrotik Inventory ===" --msgbox "$OUTPUT" 6 35
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
	IMF_CONFIG=script/imf-config
	CONFIG_CMD="--header"
	ANSWER=$(dialog --checklist "checklist" 20 35 18 \
		"SET-HOSTNAME" 1 "off" \
		"VLAN" 2 "off" \
#		"DHCP-SERVER" 3 "off" \
		"FIREWALL" 4 "off" \
		"SET-NTP" 5 "off" \
		"SIMPLE-HARDEN" 6 "off" \
		"L2TP-SERVER" 7 "off" 3>&1 1>&2 2>&3 || exit 1)

for OP in $ANSWER; do
  case "$OP" in
	SET-HOSTNAME)
		TMP=$(dialog --title "enter your device hostname" --inputbox "IMF" 8 40 3>&1 1>&2 2>&3)
		CONFIG_CMD="$CONFIG_CMD --hostname $TMP";;
	VLAN)
		CONFIG_CMD="$CONFIG_CMD --vlan"
		TMP=$(dialog --form "Enter your vlan option " 10 50 4 \
			"Vlan ID: " 1 1 "1" 1 12 20 0 \
			"Interface: " 2 1 "ether1" 2 12 20 0 3>&1 1>&2 2>&3)
		TMP1=$(echo -n $TMP | cut -d " " -f1)
		TMP2=$(echo -n $TMP | cut -d " " -f2)
		if [ $TMP1 != "" ] ; then
			CONFIG_CMD="$CONFIG_CMD --vlan-id $TMP1 "
		fi
		if [ $TMP2 != "" ] ; then
			CONFIG_CMD="$CONFIG_CMD --vlan-interface $TMP2 "
		fi
		;;

	DHCP-SERVER)
		CONFIG_CMD="$CONFIG_CMD --dhcp-server"
		TMP=$(dialog --form "Enter your dhcp option " 10 50 4 \
			"Pool: " 1 1 "192.168.1.100-192.168.1.200" 1 12 20 0 \
			"network: " 2 1 "192.168.1.0/24" 2 12 20 0 3>&1 1>&2 2>&3)
		TMP1=$(echo -n $TMP | cut -d " " -f1)
		TMP2=$(echo -n $TMP | cut -d " " -f2)
		if [ $TMP1 != "" ] ; then
			CONFIG_CMD="$CONFIG_CMD --dhcp-pool $TMP1 "
		fi
		if [ $TMP2 != "" ] ; then
			CONFIG_CMD="$CONFIG_CMD --dhcp-network $TMP2 "
		fi
		;;

  	FIREWALL)
		CONFIG_CMD="$CONFIG_CMD --firewall";;
	SET-NTP)
		TMP=$(dialog --title "enter your ntp server" --inputbox "NTP" 8 40 3>&1 1>&2 2>&3)
		CONFIG_CMD="$CONFIG_CMD --ntp-server $TMP";;
	SIMPLE-HARDEN)
		CONFIG_CMD="$CONFIG_CMD --harden";;
	ADD-ROUTE)
		CONFIG_CMD="$CONFIG_CMD --add-route";;
  	L2TP-SERVER)
		CONFIG_CMD="$CONFIG_CMD --l2tp-server";;
  *)
    echo error case: wrong input $OP
    ;;
  esac

done

if STDOUT=$(imf-config $CONFIG_CMD); then
	dialog --title "enter your device number" --inputbox "all" 8 40 2>/dev/null
	ansible-playbook -i inventory.ini mikrotik-config.yml 1>/dev/null 2>&1
	dialog --title "status of config" --msgbox "config successful :)" 5 40
else
    EXIT_CODE=$?
    dialog --title "create config status" --msgbox "$STDOUT" 6 40
    dialog --msgbox "IMF-CONFIG ERROR (Exit code: $EXIT_CODE)" 6 40
fi
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
    1 "Manange Mikrotik" \
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

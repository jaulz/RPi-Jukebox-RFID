#!/bin/bash

LOW_SOUND_FILE="/home/pi/RPi-Jukebox-RFID/misc/battery-low.mp3"
SHUTDOWN_SOUND_FILE="/home/pi/RPi-Jukebox-RFID/shared/shutdownsound.mp3"
JSON_FILE="/tmp/mupihat.json"

echo $! > /run/mupi_hat_control.pid
sleep 30

BAT_CONNECTED=$(jq -r '.BatteryConnected' ${JSON_FILE})

if [ "${BAT_CONNECTED}" -eq 1 ]; then
	while true; do
		if [ -f ${JSON_FILE} ]; then
			VBUS=$(jq -r '.Vbus' ${JSON_FILE})
            if [ "$VBUS" -le 1000 ]; then
				STATE=$(jq -r '.Bat_Stat' ${JSON_FILE})
				if [ "${STATE}" = "LOW" ]; then
					mpg123 -a hw:1,0 "$LOW_SOUND_FILE"
					echo "Battery state low"
				elif [ "${STATE}" = "SHUTDOWN" ]; then
					echo "Battery state to low - shutdown initiated"
					mpg123 -a hw:1,0 "$SHUTDOWN_SOUND_FILE"
					poweroff
				fi
			fi
		fi
		sleep 60
	done
else
	echo "No Battery connected, service stopped"
fi
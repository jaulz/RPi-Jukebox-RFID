#!/bin/bash

SOUND_FILE="/home/pi/RPi-Jukebox-RFID/misc/battery-low.mp3"
JSON_FILE="/tmp/mupihat.json"

play_sound() {
    mpg123 -a hw:1,0 "$SOUND_FILE"
}

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
					play_sound
					echo "Battery state low"
				elif [ "${STATE}" = "SHUTDOWN" ]; then
					echo "Battery state to low - shutdown initiated"
					/usr/local/bin/mupibox/./mupi_shutdown.sh ${BATTERY_LOW}
					poweroff
				fi
			fi
		fi
		sleep 60
	done
else
	echo "No Battery connected, service stopped"
fi
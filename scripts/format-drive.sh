#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

if [ "$1" != "" ]; then
    if [ "$2" != "" ]; then
        DISK_ID=$1
        PACK_ID=$2
        diskutil unmountDisk /dev/disk$DISK_ID
        echo "Writing image to disk...  (This can last more than 5 min.)"
        dd bs=1m if=raspberry-pack.img of=/dev/rdisk$DISK_ID & PID=$!

        START_TIME=$SECONDS
        while kill -0 $PID 2> /dev/null; do
            ELAPSED_TIME=$(($SECONDS - $START_TIME))
            printf "\r$ELAPSED_TIME seconds passed"
            sleep 1
        done
        printf "\rDONE\n"

        echo "Mounting disk..."
        diskutil mountDisk /dev/disk$DISK_ID
        echo "Copy files from pack..."
        cp -vr ./../packages/raspberry-pack-$PACK_ID/* /Volumes/boot
        echo "Copy files from master..."
        cp -vr ./../packages/master/* /Volumes/boot
        if [ -f ./../packages/raspberry-pack-$PACK_ID/raspberry-pack/run-before-boot.sh ]; then
            echo "Extending config.txt to allow connection with serial cable..."
            ./../packages/raspberry-pack-$PACK_ID/raspberry-pack/run-before-boot.sh
        fi
        echo "Unmounting disk"
        echo ""
        diskutil eject /dev/disk$DISK_ID
        echo ""
        printf '\e[32;5m%-6s\e[m' "NEXT STEP:"
        printf "\a Unplug SD and put it into the Raspberry Pi, and boot it!\n"
    else
        echo "please supply the name of the Raspberry-Pack template (name without 'raspberry-pack-')"
        ls -al ./../packages
    fi
else
    diskutil list
    echo "please supply drive number as parameter"
fi

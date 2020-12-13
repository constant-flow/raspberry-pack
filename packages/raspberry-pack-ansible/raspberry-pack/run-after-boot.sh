#!/bin/bash

log () { printf "\e[93m%b\e[0m" "\n=== Raspberry-Pack: $1 ===\n"; }

# run here you installation scripts ===========================================
log "Activate the generic service"

sudo cp /boot/raspberry-pack/raspberry-pack.service /lib/systemd/system/
sudo systemctl start raspberry-pack.service
sudo systemctl enable raspberry-pack.service

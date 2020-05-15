#!/bin/bash

log () { printf "\e[93m%b\e[0m" "\n=== Raspberry-Pack: $1 ===\n"; }

log "Script starter in action"
sleep 1

# enable automatic login into pi user account

log "Change to pi user"
su pi
log "add auto-login for first boot"
sudo -u pi sudo raspi-config nonint do_boot_behaviour B2
sleep 1

log "Auto login activated"

# setup raspberry-pack to start on user auto-login
printf "\nsudo /boot/raspberry-pack/raspberry-pack.sh" >> /home/pi/.bashrc

log "Raspberry-pack added to .bashrc"
sleep 1

# Reset /etc/rc.local to its original state (remove script-starter)
log "Reset /etc/rc.local if auto-starter was injected"
sudo sed -i 's+sudo bash /boot/script-starter.sh #new+# By default this script does nothing.+g' /etc/rc.local
sleep 1

# reboot
sudo reboot
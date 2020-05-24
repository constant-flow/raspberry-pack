#!/bin/bash

log () { printf "\e[93m%b\e[0m" "\n=== Raspberry-Pack: $1 ===\n"; }

init_raspberry_pack ()
{
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

    rm logstream

    # reboot
    sudo reboot
}

# setup raspberry-pack to start on user auto-login, stream all output via netcat on port 2000
if [ -f /boot/raspberry-pack/ip_of_master.conf ]; then
    REMOTE_IP=$(</boot/raspberry-pack/ip_of_master.conf)
    log "Read master's IP from file: $REMOTE_IP"
    sleep 1
else
    log "Error: Master's IP file not found"
    REMOTE_IP=127.0.0.1
fi

log "Script starter in action"
sleep 1

# enable automatic login into pi user account

log "Change to pi user"
su pi

mkfifo logstream
nc $REMOTE_IP 2000 < logstream | init_raspberry_pack &> logstream
#!/bin/bash

log () { printf "\e[93m%b\e[0m" "\n=== Raspberry-Pack: $1 ===\n"; }

loadMasterIP () {
    if [ -f /boot/raspberry-pack/ip_of_master.conf ]; then
        REMOTE_IP=$(</boot/raspberry-pack/ip_of_master.conf)
        # "Read master's IP from file: $REMOTE_IP"
        sleep 1
    else
        # "Error: Master's IP file not found"
        REMOTE_IP=127.0.0.1
    fi

    echo $REMOTE_IP
}

install_raspberry_pack () {
    # led the led blink until script is completely done
    echo timer | sudo tee /sys/class/leds/led0/trigger

    log "Mount drive for write access"
    mount -rw -o remount /
    sleep 3

    log "Setup europe time zone"
    sudo timedatectl set-timezone Europe/Berlin

    log "Wait until internet connection"

    CONNECTED=false
    for i in 1 2 3 4 5
    do
        ping -q -w 1 -c 1 `ip r | grep default | cut -d ' ' -f 3` > /dev/null && CONNECTED=true || CONNECTED=false
        if [ "$CONNECTED" = true ]; then
            echo "Connected to the internet"
            break
        fi
        sleep 5
    done

    if [ "$CONNECTED" = false ]; then
        log "No connection: maybe a reboot helps to get internet"
        sleep 3
        sudo reboot
    fi

    # install newest software packages
    log "Update / Upgrade software packages"
    sudo apt-get update && sudo apt-get upgrade -y
    sleep 1

    # Packages needs to be " " separated. Don't use linebreaks!
    if [ -f /boot/raspberry-pack/master-apt-get-packages.conf ]; then
        log "Install packages via apt-get"
        sudo apt-get install $(</boot/raspberry-pack/master-apt-get-packages.conf) -y
        sleep 1
    fi

    # Packages needs to be " " separated. Don't use linebreaks!
    if [ -f /boot/raspberry-pack/apt-get-packages.conf ]; then
        log "Install packages via apt-get"
        sudo apt-get install $(</boot/raspberry-pack/apt-get-packages.conf) -y
        sleep 1
    fi

    # Run other scripts you need to install certain things
    if [ -f /boot/raspberry-pack/run-on-boot.sh ]; then
        chmod +x /boot/raspberry-pack/run-on-boot.sh
        log "Run defined scripts"
        /boot/raspberry-pack/run-on-boot.sh
        sleep 1
    fi

    # Reset /home/pi/.bashrc (remove injected script)
    sudo sed -i 's+sudo /boot/raspberry-pack/raspberry-pack.sh++g' /home/pi/.bashrc

    log "Change user password"
    # Change the password so it's not using the default
    if [ -f /boot/raspberry-pack/user-password.conf ]; then
        if [ -f /boot/raspberry-pack/change-password.sh ]; then
            /boot/raspberry-pack/change-password.sh
            sleep 1
        fi
    fi

    # Change the hostname of the machine (find it later by <hostname>.local)
    if [ -f /boot/raspberry-pack/hostname.conf ]; then
        log "Adjust hostname"
        sudo raspi-config nonint do_hostname $(</boot/raspberry-pack/hostname.conf)
        sleep 1
    fi

    #remove auto login
    log "Turn off auto login"
    sudo raspi-config nonint do_boot_behaviour B1
    sleep 1

    #reboot for clean start
    log "Raspberry-pack installation done"

    #send udp broadcast to signal the installation is done
    HOSTNAME=$(</boot/raspberry-pack/hostname.conf)
    IP=$(hostname -I)
    log "INSTALLATION COMPLETED\n\n\aThe machine will be restarted soon so you can login via ssh:\n\t'ssh pi@${HOSTNAME}.local'\n\t'ssh pi@${IP}'\n"

    if [ -f /boot/raspberry-pack/run-after-boot.sh ]; then
        log "Additional script will be started.\n\nThe connection will drop. Wait for the green LED (ACT) to stop flashing, then the installation is done"
        /boot/raspberry-pack/run-after-boot.sh
    fi

    # reset led to default behavior
    echo mmc0 | sudo tee /sys/class/leds/led0/trigger
    rm logstream
    log "Final reboot"
    sleep 1
    sudo reboot
}

REMOTE_IP=$(loadMasterIP)
mkfifo logstream
nc $REMOTE_IP 2000 < logstream | install_raspberry_pack &> logstream
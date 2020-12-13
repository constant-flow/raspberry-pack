#!/bin/bash

log () { printf "\e[92m%b\e[0m" "\n=== Raspberry-Pack: $1 ===\n"; }
error () { printf "\e[91m%b\e[0m" "\n=== Raspberry-Pack: Error: $1 ===\n"; }
warning () { printf "\e[91m%b\e[0m" "\n=== Raspberry-Pack: Warning: $1 ===\n"; }

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

is_installed() {
    if [ "$(dpkg -l "$1" 2> /dev/null | tail -n 1 | cut -d ' ' -f 1)" != "ii" ]; then
      return 1
    else
      return 0
    fi
}

install_raspberry_pack () {
    # led the led blink until script is completely done =======================
    echo timer | sudo tee /sys/class/leds/led0/trigger

    log "Mount drive for write access"
    mount -rw -o remount /
    sleep 3

    log "Setup europe time zone"
    sudo timedatectl set-timezone Europe/Berlin

    # make sure network connection is available ===============================
    log "Check for network connection"
    CONNECTED=false
    for i in 1 2 3 4 5
    do
        ping -q -w 1 -c 1 `ip r | grep default | cut -d ' ' -f 3` > /dev/null && CONNECTED=true || CONNECTED=false
        if [ "$CONNECTED" = true ]; then
            log "Connected to network"
            break
        fi
        error "no connection. Wait 5 sec ..."
        sleep 5
    done

    if [ "$CONNECTED" = false ]; then
        log "No connection: maybe a reboot helps to get internet"
        sleep 3
        sudo reboot
    fi

    # install newest software packages ========================================
    if [ -f /boot/raspberry-pack/no-update.conf ]; then
        warning "No update nor upgrade for system packages! (FAST & DANGEROUS)"
        sleep 1
    elif [ -f /boot/raspberry-pack/update-only.conf ]; then
        log "Update software packages (no upgrade!)"
        sudo apt-get update -y
        sleep 1
    else
        log "Update / Upgrade software packages"
        sudo apt-get update && sudo apt-get upgrade -y
        sleep 1
    fi

    # install packages from master package ====================================
    if [ -f /boot/raspberry-pack/master-apt-get-packages.conf ]; then
        log "Install packages via apt-get"
        sudo apt-get install $(</boot/raspberry-pack/master-apt-get-packages.conf) -y
        sleep 1
    fi

    # install packages from selected package ==================================
    if [ -f /boot/raspberry-pack/apt-get-packages.conf ]; then
        log "Install packages via apt-get"
        sudo apt-get install $(</boot/raspberry-pack/apt-get-packages.conf) -y
        sleep 1
    fi

    # Run other scripts you need to install certain things ====================
    if [ -f /boot/raspberry-pack/run-on-boot.sh ]; then
        chmod +x /boot/raspberry-pack/run-on-boot.sh
        log "Run defined scripts"
        /boot/raspberry-pack/run-on-boot.sh
        sleep 1
    fi

    # Reset /home/pi/.bashrc (remove injected script) =========================
    sudo sed -i 's+sudo /boot/raspberry-pack/raspberry-pack.sh++g' /home/pi/.bashrc

    log "Change user password"
    # Change the password so it's not using the default =======================
    if [ -f /boot/raspberry-pack/user-password.conf ]; then
        if [ -f /boot/raspberry-pack/change-password.sh ]; then
            /boot/raspberry-pack/change-password.sh
            sleep 1
        fi
    fi

    # Change the hostname of the machine (find it later by <hostname>.local) ==
    if [ -f /boot/raspberry-pack/hostname.conf ]; then
        log "Adjust hostname"
        sudo raspi-config nonint do_hostname $(</boot/raspberry-pack/hostname.conf)
        sleep 1
    fi

    # set auto login ==========================================================
    AUTO_LOGIN="off"
    if [ -f /boot/raspberry-pack/autologin.conf ]; then
        AUTO_LOGIN="on"
    fi

    GUI_PACKAGE_OUTPUT=$(dpkg -l xserver-xorg)
    if [[ $GUI_PACKAGE_OUTPUT == *"<none>"* ]]; then
    echo "It's no GUI system"
        # auto login to CLI active (B1 = autologin off)
        if [[ $AUTO_LOGIN == *"on"* ]]; then
            echo "auto-login: on"
            sudo -u pi sudo raspi-config nonint do_boot_behaviour B2
        else
            echo "auto-login: off"
            sudo -u pi sudo raspi-config nonint do_boot_behaviour B1
        fi
    else
        echo "It's a GUI system"
        # auto login to GUI active (B3 = autologin off)
        if [[ $AUTO_LOGIN == *"on"* ]]; then
            echo "auto-login: on"
            sudo -u pi sudo raspi-config nonint do_boot_behaviour B4
        else
            echo "auto-login: off"
            sudo -u pi sudo raspi-config nonint do_boot_behaviour B3
        fi
        sudo dpkg-reconfigure lightdm
    fi
    sleep 1

    # enable VNC ==============================================================
    if [ -f /boot/raspberry-pack/enable-vnc.conf ]; then
        log "Enable VNC remote connection"
        if is_installed realvnc-vnc-server || apt-get install realvnc-vnc-server; then
            sudo systemctl enable vncserver-x11-serviced.service &&
            sudo systemctl start vncserver-x11-serviced.service
        fi
        sleep 1
    fi


    # run last phase of installation ==========================================
    log "Raspberry-pack installation done"

    #send udp broadcast to signal the installation is done
    HOSTNAME=$(</boot/raspberry-pack/hostname.conf)
    IP=$(hostname -I)
    log "INSTALLATION COMPLETED\n\n\aThe machine will be restarted soon so you can login via ssh:\n\t'ssh pi@${HOSTNAME}.local'\n\t'ssh pi@${IP}'\n"

    if [ -f /boot/raspberry-pack/run-after-boot.sh ]; then
        log "Additional script will be started.\n\nThe connection will drop. Wait for the green LED (ACT) to stop flashing, then the installation is done"
        /boot/raspberry-pack/run-after-boot.sh
    fi

    # register a service to run at every boot of the system
    if [ -f /boot/raspberry-pack/service-starter.sh ]; then
        log "Activate the generic service to start 'service-starter.sh'"

        sudo cp /boot/raspberry-pack/raspberry-pack.service /lib/systemd/system/
        sudo systemctl start raspberry-pack.service
        sudo systemctl enable raspberry-pack.service
    fi

    # reset led to default behavior ===========================================
    echo mmc0 | sudo tee /sys/class/leds/led0/trigger
    rm logstream
    log "Final reboot"
    sleep 1
    sudo reboot
}

REMOTE_IP=$(loadMasterIP)

log "Check for network connection"
CONNECTED=false
for i in 1 2 3 4 5
do
    ping -q -w 1 -c 1 `ip r | grep default | cut -d ' ' -f 3` > /dev/null && CONNECTED=true || CONNECTED=false
    if [ "$CONNECTED" = true ]; then
        log "Connected to network"
        break
    fi
    error "no connection. Wait 5 sec ..."
    sleep 5
done

# create named pipe to log into that transmits the install_raspberry_pack logs
echo "Transmit the terminal output to: ${REMOTE_IP}"
mkfifo logstream
nc $REMOTE_IP 2000 < logstream | install_raspberry_pack &> logstream
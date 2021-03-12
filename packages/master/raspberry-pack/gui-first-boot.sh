#!/bin/bash

# remove wizard at first gui boot and turn off autostart script ===============
if [ -f /etc/xdg/autostart/piwiz.desktop ]; then
    if [ -f /boot/raspberry-pack/keep-gui-wizard.conf ]; then
        echo "Raspberry Pis Gui wizard will be left untouched"
        echo "wizard not removed" >> /home/pi/raspberry-pack.log
    else
        echo "Remove Raspberry Pis Gui wizard"
        sudo rm /etc/xdg/autostart/piwiz.desktop
        echo "wizard removed" >> /home/pi/raspberry-pack.log
    fi

    # recover autostart to default from backed-up file (turn off this script here)
    sudo mv /etc/xdg/lxsession/LXDE-pi/autostart.bak /etc/xdg/lxsession/LXDE-pi/autostart

    # run package defined script (may wants to add something to the autostart)
    if [ -f /boot/raspberry-pack/run-on-gui-boot.sh ]; then
        /boot/raspberry-pack/run-on-gui-boot.sh
    fi

    # reboot system to effectively apply changes (e.g. remove the wizard)
    sudo reboot

else
    echo "No gui found yet"
    echo "No gui found yet" >> /home/pi/raspberry-pack.log
fi
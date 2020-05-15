#!/bin/bash
# NO MODIFICATIONS NEEDED

# cat /boot/raspberry-pack/user-password.conf
PASSWORD=$(</boot/raspberry-pack/user-password.conf)
printf "raspberry\n${PASSWORD}\n${PASSWORD}" | (sudo -u pi passwd pi)
sudo rm /boot/raspberry-pack/user-password.conf -f
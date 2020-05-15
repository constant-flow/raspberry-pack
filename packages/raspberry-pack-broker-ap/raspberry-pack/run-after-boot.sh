#!/bin/bash

log () { printf "\e[93m%b\e[0m" "\n=== Raspberry-Pack: $1 ===\n"; }

# communicate it will take a bit longer
printf "\nThe Access Point will be started now, thus the connection will be cut. \nThis can take some time ... wait for the Wifi to show up\n" | nc -b -u 255.255.255.255 13337 & sleep 1;

# Guides:
# https://frillip.com/using-your-raspberry-pi-3-as-a-wifi-access-point-with-hostapd/
# https://learn.sparkfun.com/tutorials/setting-up-a-raspberry-pi-3-as-an-access-point/all

sudo apt-get install dnsmasq hostapd -y

# Setup dhcp: remove wlan0 from its control ===================================
sudo sh -c 'echo "denyinterfaces wlan0" >> /etc/dhcpcd.conf'
sudo service dhcpcd restart

# Copy hostapd ================================================================
log "setup hostapd"
sudo cp /boot/raspberry-pack/hostapd.conf /etc/hostapd/hostapd.conf
sudo sh -c 'echo "DAEMON_CONF=\"/etc/hostapd/hostapd.conf\"" >> /etc/default/hostapd'
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sleep 2
sudo service hostapd start

# copy dnsmasq config =========================================================
log "setup dnsmasq"
sudo cp /boot/raspberry-pack/dnsmasq.conf /etc/dnsmasq.conf
sudo service dnsmasq start

sleep 2
# Configure wlan0 network with static IP ======================================
log "setup static IP"
sudo sh -c 'echo "allow-hotplug wlan0
iface wlan0 inet static
    address 172.24.1.1
    netmask 255.255.255.0
    network 172.24.1.0
    broadcast 172.24.1.255" >> /etc/network/interfaces'

# TODO: We should take the network up and down but that is not a good idea while we are connected via ssh
log "restart wifi"
sudo ifdown wlan0; 
sleep 2
sudo ifup wlan0;
sleep 2
# sudo reboot # this is done by the subsequent script

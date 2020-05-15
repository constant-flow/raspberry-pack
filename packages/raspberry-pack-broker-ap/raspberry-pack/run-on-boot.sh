#!/bin/bash
# run here you installation scripts ===========================================

# Copy mosquitto.conf =========================================================
sudo cp /boot/raspberry-pack/mosquitto.conf /etc/mosquitto/mosquitto.conf
sudo service mosquitto start
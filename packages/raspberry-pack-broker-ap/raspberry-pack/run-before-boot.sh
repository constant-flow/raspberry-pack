#!/bin/bash
echo "dtoverlay=pi3-disable-bt
dtoverlay=pi3-miniuart-bt" >> /Volumes/boot/config.txt

echo "Disable bluetooth for Raspberry Pi 3"
echo "Debugging connection: serial cable at screen /dev/tty.usbserial 115200"

#!/bin/bash
curl -L https://downloads.raspberrypi.org/raspbian_lite_latest -o temp.zip
unzip temp.zip
rm temp.zip
mv *.img raspberry-pack.img
sleep 3
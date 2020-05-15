# NO MODIFICATIONS NEEDED
passwd pi << EOF
raspberry
$(</boot/raspberry-pack/user-password.conf)
$(</boot/raspberry-pack/user-password.conf)
EOF
sudo rm /boot/raspberry-pack/user-password.conf -f
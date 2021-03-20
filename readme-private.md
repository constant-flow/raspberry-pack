# TESTS

# pahas/snapcast reduce latency

- `sudo nano /etc/systemd/system/a2dp-playback.service` change to
- `ExecStart=/usr/bin/bluealsa-aplay --pcm-buffer-time=20000 --pcm-period-time=10000 --profile-a2dp 00:00:00:00:00:00`

# similar packages to raspberry-pack

https://github.com/nmcclain/raspberian-firstboot
https://github.com/meeDamian/raspios

# service starter

- move to non-boot location when booting

https://thinkl33t.co.uk/deploying-a-raspberry-pi-chromium-kiosk-using-ansible/

# create tutorial project

# create template project

# create a project using file crispr

# change splash screen

`/usr/share/plymouth/themes/pix/splash.png`

# no rainbow at boot

`disable_splash=1 to config.txt (no rainbow).`

# copy public key to ~/.ssh/authorized_keys

- https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md

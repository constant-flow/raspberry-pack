# Raspberry-Pack

| ![raspberry-pack.png](assets/raspberry-pack.png) | **Why Raspberry-Pack:** Don't flash each Raspberry Pi by hand, but automate things and make it reusable, and all that headlessly: No keyboard, no mouse, no monitor, no ssh needed.<br><br> **Headless, easy, fast and reproducible** |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

![CLI](assets/example-cli.png)

# What is is good for?

- Raspberry-Packs bundle a specific setup you want to clone/roll out on multiple devices or you want to share with friends or the internet
- It installs packages, runs scripts, setup services on your Raspberry Pi similar to a configured image
- Its aim is to reduce the manual overhead of installing scripts by hand with automation
- Raspberry-Packs can be added from a public git repository (e.g. [example](https://github.com/constant-flow/raspberry-pack-apache2), [all promoted](promoted-packages.md)). These packages will check for updates on every execution of Raspberry-Pack
- Raspberry-Packs can be used locally. Simply create a folder named `raspberry-pack-*` inside the `packages` directory

# Why not using an image

- In contrast to an image, a Raspberry-Pack installs an official distribution image first and based on that the rest
- Every installation step and change is comprehensible upfront, whereas an image is a blackbox where you have no clue what was installed and done. Thus it's modular and developers can copy interesting sections from other Raspberry-Packs
- Images are huge and hard to trim down, Raspberry-Packs are tiny scripts and links to downloads
- Raspberry-Packs are flexible e.g. WiFi or hostname are adjustable via the wizard. Adjusting a Raspberry-Pack is done in a text editor and doesn't require an export.
- At installations it does the updating and upgrading automatically, so you always start with a solid OS

# How to use Raspberry-Pack

Raspberry-Pack is designed for use with [Raspberry Pi](http://www.raspberrypi.org) version 1-4

## The step by step wizard guides you through the installation process

- download raspbian image
- select and configure package
- flash to SD
- boot your RPi
- informs you when the install is done
- helps how to connect to it via ssh (not required)

## Getting started

```
# clone the project
git clone git@github.com:constant-flow/raspberry-pack.git

# install Raspberry-Pack tool
pip install -r requirements.txt

# run Raspberry-Pack wizard
python wizard.py
```

> **Raspberry-Pack relies on [Python 3](https://docs.python-guide.org/starting/install3/osx/), try using `pip3` and `python3` when encountering issues**
>
> **MAC/OSX supported only (No Windows or Linux support)**

## Create your own Raspberry-Pack

Create a folder inside `packages/`. Each package name has the prefix `raspberry-pack-`.

| Filename                   | required | where / when      | use                                                                                                               |
| -------------------------- | -------- | ----------------- | ----------------------------------------------------------------------------------------------------------------- |
| `readme.md`                | ✔        | Host              | documentation & description for that package                                                                      |
| `raspberry-pack.md`        | ✔        | Host / Wizard     | short description for that package - used when listing all packages                                               |
| `📦/env-inquirer.yaml`     |          | Host / Wizard     | yaml file to ask for package specific input in the wizard – [more info](env-inquirer.md)                          |
| `📦/run-before-boot.sh`    |          | Host / Wizard     | script to run when the SD flashing is done. Executed on your Mac, e.g. to alter the config.txt on SD              |
| `📦/apt-get-packages.conf` |          | RPi / first boot  | space-separated list of packages to install via `sudo apt-get install`                                            |
| `📦/hostname.conf`         |          | RPi / first boot  | defines hostname                                                                                                  |
| `📦/user-password.conf`    |          | RPi / first boot  | defines user's (`pi`) password                                                                                    |
| `📦/autologin.conf`        |          | RPi / first boot  | when this file exists, the system will login automatically (CLI/GUI)                                              |
| `📦/no-update.conf`        |          | RPi / first boot  | when this file exists, the system will not update system packages (only use during development)                   |
| `📦/update-only.conf`      |          | RPi / first boot  | when this file exists, the system will only update system packages                                                |
| `📦/enable-vnc.conf`       |          | RPi / first boot  | when this file exists, the system will be connectable via VNC (virtual Network Computing)                         |
| `📦/keep-gui-wizard.conf`  |          | RPi / first boot  | when this file exists, the system will keep the Raspberry GUI wizard on startup                                   |
| `📦/run-on-boot.sh`        |          | RPi / first boot  | script to run after updating and installing apt packages                                                          |
| `📦/run-after-boot.sh`     |          | RPi / second boot | script to run after the "installation done"-signal. Useful, when connection will drop                             |
| `📦/run-on-gui-boot.sh`    |          | RPi / gui boot    | script to run after the the first time when the Raspberry boots to the graphical interface (used for GUI OS only) |
| `📦/service-starter.sh`    |          | RPi / every boot  | when this file exists, this script is called via a service at every boot of the Raspberry                         |
| `📦/*`                     |          | RPi / any script  | add all your files you need for your script in here. In your script you can access it here `/boot/📦/*`           |

> 📦 = `raspberry-pack`
>
> If you don't need a certain `\*.conf` or `*.sh` file, better delete it, than leaving it empty. Keep things tidy.
>
> Take care your script doesn't need user interaction, use command parameters, piping and other tricks to achieve required inputs

# Development

## Ressources

- [`raspi-config` commandline options](https://github.com/RPi-Distro/raspi-config/blob/master/raspi-config)
- [Updating and Upgrading RPi](https://www.raspberrypi.org/documentation/raspbian/updating.md)
- [Configuration options Rpi](https://www.raspberrypi.org/documentation/configuration/)
- [Older images of raspbian](https://downloads.raspberrypi.org/raspbian/images/)

## Our logo

- Our logo is a remix of the trademark's logo of [Raspberry Pi](http://www.raspberrypi.org)
- Raspberry-Pack is no official product of Raspberry Pi
- Next to our license also check their [Trademark Rules](https://www.raspberrypi.org/trademark-rules/)

## Your contribution

- You are welcome to submit merge requests for packages you created and consider useful for a broader audience
- Found a bug, report it as an issue
- If you port it for windows / linux, we are more than happy to provide it to everyone 🤗

> **Donation**
>
> In case you like Raspberry-Pack and want to support the project financially you can donate as the project is created in free time
>
> [![Donate with PayPal](https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ZDMVW94NZ84GU)

# Changelog

## `Version 0.1.0`

### Improvements

- add remote Raspberry-Packs from a remote git repository [more...](promoted-packages.md)
- allow Packs to ask for user's input - input will be available as environment variables [more...](env-inquirer.md)
- run a script when booted to the Raspberry OS GUI (`run-on-gui-boot.sh`)
- disabled wizard at first boot

### Bugfixes

- try multiple times to connect to the network
- repeat Raspberry-Pack installation on reboot when connectivity was missing

#!/usr/bin/env pyth
# from __future__ import print_function, unicode_literals
from PyInquirer import prompt  # , print_json

import glob
import os
import re
import sys

# =============================================================================


def hl():  # prints a horizontal line
    print("────────────────────────────────────────────────────────────────────────────────")


def printIntro():
    os.chdir(startLocation)
    os.system('clear')
    os.system("cat ./assets/raspberry-pack.art")
    print("\nRaspberry-Pack helps you to setup your Raspberry in no time.\nNo keyboard, mouse, monitor or ssh needed!\n\n This tool helps to:\n ═══════════════════\n 1.) Download the newest raspbian image\n 2.) Select a pre-configured package\n 3.) flash your SD card\n 4.) informs you, when everything is done\n 5.) gives you the RPi`s IP and hostname so you can SSH into it\n")
    print(" (To navigate use arrow keys, enter and space)")
    print(" (Don't use mouse clicks! ¯\_(ツ)_ /¯ issue: # 10)\n")
    print("Make sure you have inserted an SD card.")


def checkForFlashableImage():
    os.chdir(startLocation)
    imageExists = os.path.exists('./scripts/raspberry-pack.img')

    if imageExists:
        refreshExistingImage = [
            {
                'type': 'confirm',
                'message': "🗑️  An existing Raspbian image was found.\n     Do you want to download the most recent version of Raspbian?",
                'name': 'refreshImage',
                'default': False,
            },
        ]
        refreshImage = prompt(refreshExistingImage)

        if refreshImage['refreshImage']:
            os.chdir("./scripts")
            os.system('rm raspberry-pack.img')
            os.system('./download-image.sh')
            os.system('python upgrade-image.py')
    else:
        downloadQuestion = [
            {
                'type': 'confirm',
                'name': 'downloadQuestion',
                'message': '📥 No Raspbian image found. Do you want to download it?\n     (You need around 3 GB of free disk space)',
                'default': True
            },
        ]
        doDownload = prompt(downloadQuestion)

        if doDownload['downloadQuestion']:
            print("\n Start Download:\n ═══════════════\n")
            os.chdir("./scripts")
            os.system('./download-image.sh')
            os.system('python upgrade-image.py')
        else:
            hl()
            print(
                "❌ Raspberry-Pack installation was canceled. Free up space and come back.")
            hl()
            sys.exit()


def shortenPackagePlusDescripton(p):
    description = "[No description]"
    readmePath = './'+p+'readme.md'

    # shorten name (without prefix and end-slash)
    shortPackageName = p[15:]
    shortPackageName = re.sub('\/', '', shortPackageName)

    # add description
    if os.path.exists(readmePath):
        maxChars = 80
        readmeFile = open(readmePath, 'r')

        description = readmeFile.readline()
        remainingChars = maxChars - 4 - \
            len(shortPackageName) - len(packageDescriptionSeparator)
        if len(description) > remainingChars:
            description = description[:remainingChars]+"…"

        readmeFile.close()

    return shortPackageName + packageDescriptionSeparator + description


packageDescriptionSeparator = " -> "


def selectPackage():
    os.chdir(startLocation)
    os.chdir("./packages")
    packages = glob.glob("**/")
    packages.remove('master/')
    packages.remove('untested/')

    packages = map(shortenPackagePlusDescripton, packages)

    packageQuestion = [
        {
            'type': 'list',
            'name': 'package',
            'message': '📦 Choose the package to install',
            'choices': packages
        },
    ]

    packageAnswer = prompt(packageQuestion)

    # get rid of description and make name long again
    packageAnswer['package'] = 'raspberry-pack-' + \
        packageAnswer['package'].split(packageDescriptionSeparator)[0]+"/"

    packageShortName = re.sub('raspberry-pack-', '', packageAnswer['package'])
    packageShortName = re.sub('\/', '', packageShortName)

    packageAnswer['package'] = "raspberry-pack-"+packageShortName+"/"
    return [packageAnswer, packageShortName]


def selectDisk():
    print("[0;35m  \n Available Disks:\n ════════════════\n [0m")
    cmdListDrives = 'diskutil list physical'
    os.system(cmdListDrives)

    hl()

    volumeQuestion = [
        {
            'type': 'input',
            'name': 'volumeNumber',
            'message': '💾 Choose the disk to flash from the list shown above.\n     In case you don\'t see a matching disk (name / size),\
  \n     enter nothing and confirm.\n\n     Only give a number (e.g. for "disk4" enter "4").',
        },
    ]
    volumeAnswer = prompt(volumeQuestion)
    if volumeAnswer['volumeNumber'] == "0" or volumeAnswer['volumeNumber'] == "1":
        print("Seem like you try to overwrite a system drive. We stopped you doing so!")
        sys.exit(4)

    if volumeAnswer['volumeNumber'] == "" or volumeAnswer['volumeNumber'] == " ":
        hl()
        print("🧐 You canceled. \n\n   Missed your drive?\n   Maybe check if your drive is mounted properly \n   tip: unplug, wait some seconds and replug it")
        hl()
        sys.exit()

    return volumeAnswer


def flashDrive():
    flashDriveQuestion = [
        {
            'type': 'confirm',
            'message': "❗ By confirming with 'Y', you'll overwrite and flash disk" + volumeAnswer['volumeNumber']+" with\n     " + packageAnswer['package'] + " after confirming with your password.\n\n     Do you want to continue?\n\n⚠️    ║ Disclaimer: Only proceed if you know what you are doing!\n     ║ Entering the wrong disk number may end in complete data loss on your\n     ║ machine or a connected drive!\n\n   ",
            'name': 'finalConfirmation',
            'default': False,
        },
    ]

    os.chdir(startLocation)
    os.chdir("./scripts")
    cmdFormatDrive = "sudo ./format-drive.sh " + \
        volumeAnswer['volumeNumber'] + " " + packageShortName

    finalConfirmation = prompt(flashDriveQuestion)

    hl()
    if finalConfirmation['finalConfirmation']:
        print("Raspberry-Pack installation starts")
        os.system(cmdFormatDrive)

    else:
        print("❌ Raspberry-Pack installation was canceled. Nothing happened.")
        hl()
        sys.exit()


def waitForRaspberryToRespond():
    print("\n\n🥚 Waiting for the Raspberry Pi to complete the installation\n(This can take several minutes): ...\n")
    cmdWaitForNetcarResponse = "nc -lu 13337"
    os.system(cmdWaitForNetcarResponse)


def setWiFiCredentials():
    os.chdir(startLocation)
    os.chdir("packages/" + packageAnswer['package'])

    wifiConfigExists = os.path.exists('./wpa_supplicant.conf')

    currentSSID = ""
    currentPassphrase = ""

    if wifiConfigExists:
        with open('wpa_supplicant.conf') as openfileobject:
            for line in openfileobject:
                if line.find("ssid") != -1:
                    entries = line.split('"')
                    currentSSID = entries[1]
                if line.find("psk") != -1:
                    entries = line.split('"')
                    currentPassphrase = entries[1]

    wifiQuestion = [
        {
            'type': 'input',
            'name': 'ssid',
            'message': '📡 What Wi-Fi should the Raspberry connect to?',
            'default': currentSSID

        }, {
            'type': 'password',
            'name': 'wifi-pass',
            'message': '🔐 What\'s the Wi-Fi\'s passphrase?',
            'default': currentPassphrase
        }
    ]
    wifiAnswer = prompt(wifiQuestion)

    fileWifi = open('wpa_supplicant.conf', 'w+')
    fileWifi.write('\
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n\
update_config=1\n\
country=DE\n\
\n\
network={\n\
    ssid="'+wifiAnswer['ssid']+'"\n\
    psk="'+wifiAnswer['wifi-pass']+'"\n\
}')
    fileWifi.truncate()
    fileWifi.close()


def setHostname():
    hostnameFilePath = './hostname.conf'
    os.chdir(startLocation)

    os.chdir("packages/" + packageAnswer['package']+"raspberry-pack/")

    hostname = "raspberry-pack"
    if os.path.exists(hostnameFilePath):
        with open(hostnameFilePath) as hostnameFile:
            hostname = hostnameFile.readline()

    hostnameQuestion = [
        {
            'type': 'input',
            'name': 'hostname',
            'message': '🏷  What the hostname for this Raspberry?',
            'default': hostname
        }
    ]
    hostnameAnswer = prompt(hostnameQuestion)

    hostname = hostnameAnswer['hostname']

    hostnameFile = open(hostnameFilePath, 'w+')
    hostnameFile.seek(0)
    hostnameFile.write(hostname)
    hostnameFile.truncate()
    hostnameFile.close()


def setPassword():
    passwordFilePath = './user-password.conf'
    os.chdir(startLocation)

    os.chdir("packages/" + packageAnswer['package']+"raspberry-pack/")

    password = "raspberrypack"
    if os.path.exists(passwordFilePath):
        with open(passwordFilePath) as passwordFile:
            password = passwordFile.readline()

    passwordQuestion = [
        {
            'type': 'input',
            'name': 'password',
            'message': '🔐 What the password for this Raspberry?',
            'default': password
        }
    ]
    passwordAnswer = prompt(passwordQuestion)

    password = passwordAnswer['password']

    passwordFile = open(passwordFilePath, 'w+')
    passwordFile.seek(0)
    passwordFile.write(password)
    passwordFile.truncate()
    passwordFile.close()

# =============================================================================


startLocation = os.getcwd()

printIntro()
hl()

checkForFlashableImage()
hl()

[packageAnswer, packageShortName] = selectPackage()
hl()

setWiFiCredentials()
hl()

setHostname()

setPassword()
hl()

volumeAnswer = selectDisk()
hl()

flashDrive()
hl()

waitForRaspberryToRespond()
sys.exit()

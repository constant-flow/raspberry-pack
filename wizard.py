#!/usr/bin/env python3
# from __future__ import print_function, unicode_literals
from PyInquirer import prompt  # , print_json

import glob
import os
import re
import sys
from giturlparse import parse
import yaml
from sys import platform

# =============================================================================


def hl():  # prints a horizontal line
    print("────────────────────────────────────────────────────────────────────────────────")

def exitprompt():
    exitQuestion = [
            {
                'type': 'confirm',
                'message': "❌ Do you want to exit?",
                'name': 'exit',
                'default': False,
            },
        ]

    exitAnswer = prompt(exitQuestion)

    if exitAnswer == {} or exitAnswer["exit"]:
        exit(0)
    
    print()



def promptSecurely(questions, quitOnEmptyInput=True):
    while True:
        reply = prompt(questions)
        if not reply == {}:
            break
        else:
            if quitOnEmptyInput:
                exitprompt()
            else:
                print("🎹 Please use the keyboard. Quit with 'Cancel'\n")
    return reply


def printIntro():
    os.chdir(startLocation)
    os.system('clear')
    os.system("cat ./assets/raspberry-pack.art")
    print("\nRaspberry-Pack helps you to setup your Raspberry in no time.\nNo keyboard, mouse, monitor or ssh needed!\n\n This tool helps to:\n ═══════════════════\n 1.) Download the newest OS image\n 2.) Select a pre-configured package\n 3.) flash your SD card\n 4.) informs you, when everything is done\n 5.) gives you the RPi`s IP and hostname so you can SSH into it\n")
    print(" (To navigate use arrow keys, enter and space)")
    print("Make sure you have inserted an SD card.")


imagesToInstall = ["https://downloads.raspberrypi.org/raspios_lite_armhf_latest", "https://downloads.raspberrypi.org/raspios_armhf_latest", "https://downloads.raspberrypi.org/raspios_full_armhf_latest", "Cancel"]

def checkForFlashableImage():
    os.chdir(startLocation)
    imageExists = os.path.exists('./scripts/raspberry-pack.img')

    downloadFreshImage = False
    versionHint = "No version recorded, better reinstall"

    import subprocess
    imageVersionPath = './scripts/raspberry-pack.img.version'
    imageVersionExists = os.path.exists(imageVersionPath)

    if imageVersionExists:
        versionHint = subprocess.check_output('cat '+imageVersionPath, shell=True).decode('UTF-8').rstrip()

    if imageExists:
        refreshExistingImage = [
            {
                'type': 'confirm',
                'message': "🗑️  An existing OS image was found (version: "+versionHint+").\n     Do you want to download the most recent or a different OS version?",
                'name': 'refreshImage',
                'default': False,
            },
        ]
        refreshImage = promptSecurely(refreshExistingImage)

        downloadFreshImage = refreshImage['refreshImage']

    if not imageExists or downloadFreshImage:
        hl()
        downloadQuestion = [
            {
                'type': 'list',
                'name': 'imageUrl',
                'message': '📥 Which OS version to install?\n     (You need around 3 GB of free disk space)',
                'choices': imagesToInstall
            },
        ]

        imageDownload = promptSecurely(downloadQuestion, False)

        print(imageDownload)

        if imageDownload['imageUrl'] == 'Cancel':
            hl()
            print(
                "❌ Raspberry-Pack installation was canceled. Free up space and come back.")
            hl()
            sys.exit()
        else:
            url = imageDownload['imageUrl']
            print("\n Start Download:\n ═══════════════\n")
            os.chdir("./scripts")
            os.system('./download-image.sh -url ' + url)
            os.system('python upgrade-image.py')



def shortenPackagePlusDescripton(p):
    description = "[No description]"
    readmePath = './'+p+'raspberry-pack.md'
    gitPath = './'+p+'.git'

    # shorten name (without prefix and end-slash)
    shortPackageName = p[15:]
    shortPackageName = re.sub('\/', '', shortPackageName)

    # check if is a git based package
    isGitPackage = os.path.exists(gitPath)

    # add description
    if os.path.exists(readmePath):
        maxChars = 80
        readmeFile = open(readmePath, 'r')

        description = readmeFile.readline()
        description = re.sub('\n', '', description)

        if isGitPackage:
            description = "🟢 " + description
        else:
            description = "🔴 " + description

        remainingChars = maxChars - 4 - \
            len(shortPackageName) - len(packageDescriptionSeparator)
        if len(description) > remainingChars:
            description = description[:remainingChars]+"…"

        readmeFile.close()

    return shortPackageName + packageDescriptionSeparator + description


packageDescriptionSeparator = " → "
customRepoLink = "[ADD GIT REPO]" + packageDescriptionSeparator + "Provide a git link to a Raspberry-Pack"

def updatePackages():

    print("Check for updated packages:\n")

    os.chdir(startLocation)
    os.chdir("./packages")
    packages = glob.glob("raspberry-pack-*/")

    checkedGitRepos = 0

    for package in packages:
        os.chdir(startLocation)
        os.chdir("./packages")
        if os.path.exists(package + "/.git"):
            os.chdir("./" + package)
            os.system("git config pull.ff only")
            os.system("git pull")
            checkedGitRepos = checkedGitRepos+1

    if checkedGitRepos > 0:
        print("Found "+str(checkedGitRepos)+" git based repositories, updated to newest version")

def selectPackage():
    os.chdir(startLocation)
    os.chdir("./packages")
    packages = glob.glob("raspberry-pack-*/")

    packages = map(shortenPackagePlusDescripton, packages)
    packages = list(packages)
    packages.append(customRepoLink)

    packageQuestion = [
        {
            'type': 'list',
            'name': 'package',
            'message': '📦 Choose the package to install',
            'choices': packages
        },
    ]

    packageAnswer = promptSecurely(packageQuestion)

    packageShortName = ""

    if packageAnswer['package'] == customRepoLink:
        customPackageQuestion = [
            {
                'type': 'input',
                'name': 'repoUrl',
                'message': '🌐 What the packages repo url?',
                'default': ""
            }
        ]

        customPackage = promptSecurely(customPackageQuestion)
        url = customPackage['repoUrl']
        urlParts = url.split('/')
        projectName = urlParts[len(urlParts)-1]

        if not projectName.find("raspberry-pack-") == 0:
            projectName = 'raspberry-pack-' + projectName

        projectName = re.sub('.git', '', projectName)

        if not parse(url).valid:
            sys.exit("Stopped as a malformed url was provided: " + projectName)

        os.system('git clone --depth 1 '+ url + ' '+ projectName)
        packageAnswer['package'] = projectName + "/"

        packageShortName = re.sub('raspberry-pack-', '', projectName)
        packageShortName = re.sub('\/', '', packageShortName)

        if not os.path.exists("./"+projectName+"/raspberry-pack/"):
            os.system('rm -rf ./'+projectName)
            sys.exit("No valid Raspberry-Pack selected (raspberry-pack folder missing), delete wrong data and cancel wizard")

    else:
        # get rid of description and make name long again
        packageAnswer['package'] = 'raspberry-pack-' + \
            packageAnswer['package'].split(packageDescriptionSeparator)[0]+"/"

        packageShortName = re.sub('raspberry-pack-', '', packageAnswer['package'])
        packageShortName = re.sub('\/', '', packageShortName)

        packageAnswer['package'] = "raspberry-pack-"+packageShortName+"/"
    return [packageAnswer, packageShortName]

def enterPackageVariables():
    packageName = packageAnswer['package']
    os.chdir(startLocation)

    pathOfPackageQuestions = "./packages/" + packageName + "raspberry-pack/env-inquirer.yaml"
    pathOfEnvFile = "./packages/" + packageName + "raspberry-pack/.env"

    if not os.path.exists(pathOfPackageQuestions):
        return

    if os.path.exists(pathOfEnvFile):
        print("[0;35m\n═══ Current .env file: ═══[0m")
        with open(pathOfEnvFile, 'r') as f:
            print(f.read())

        overwriteEnvFileQuestion = [
            {
                'type': 'confirm',
                'message': "These environment variables are already existing.\n  Do you want to overwrite them?",
                'name': 'overwriteEnv',
                'default': False,
            }
        ]

        overwriteEnvFileQuestionAnswer = promptSecurely(overwriteEnvFileQuestion)
        if not overwriteEnvFileQuestionAnswer["overwriteEnv"]:
            return


    with open(pathOfPackageQuestions, 'r') as stream:
        try:
            questions = yaml.safe_load(stream)
            environmentVarsAnswers = promptSecurely(questions["environmentVars"])
            envFile = open(pathOfEnvFile, 'w+')

            for key in environmentVarsAnswers:
                value = environmentVarsAnswers[key]
                if isinstance(value, list):
                    valueSeparator = ","
                    value = valueSeparator.join(value)
                envFile.write(key + "='" + value + "'\n")

            envFile.truncate()
            envFile.close()

        except yaml.YAMLError as exc:
            print(exc)

def makeDriveOption(driveLine):
    elements = driveLine.split()
    if len(elements) < 2:
        return ""
    return elements[0] + "    (Size:"+ elements[1] + ")"
    

def selectDisk():
    print("[0;35m  \n Available Disks:\n ════════════════\n [0m")
    cmdListDrives = ''
    cmdListDrivesHuman = ''
    driveOptions = []

    if platform == "linux" or platform == "linux2":
        # linux
        cmdListDrivesHuman = 'lsblk -p -o NAME,SIZE,MOUNTPOINT,RM,RM | grep "1  1"'
        cmdListDrives = 'lsblk -p -o NAME,SIZE,RM,RM,MOUNTPOINT | grep --color=never "1  1" | grep -v "media"'
        drives = os.popen(cmdListDrives).read().split("\n")

        driveOptions = map(makeDriveOption, drives)
        driveOptions = filter(lambda x: not x=="", driveOptions)

    elif platform == "darwin":
        # mac
        cmdListDrivesHuman = 'diskutil list physical'
        cmdListDrives = 'diskutil list physical'


        
    #elif platform == "win32":
    #   cmdListDrives = 'echo "windows is not supported; exit(1);"'

    if cmdListDrives == '':
        print(" ❌ Sorry, your OS is not supported. \n")
        exit(1)

    os.system(cmdListDrivesHuman)

    hl()

#     volumeQuestion = [
#         {
#             'type': 'input',
#             'name': 'volumeNumber',
#             'message': '💾 Choose the disk to flash from the list shown above.\n     In case you don\'t see a matching disk (name / size),\
#   \n     enter nothing and confirm.\n\n     Only give a number (e.g. for "disk4" enter "4").',
#         },
#     ]

    volumeQuestion = [
        {
            'type': 'list',
            'name': 'volumeNumber',
            'message': '💾 Choose the disk to flash from the list shown above.\n     In case you don\'t see a matching disk (name / size),\
  \n     enter nothing and confirm.\n\n     Only give a number (e.g. for "disk4" enter "4").',
            'choices': driveOptions
        },
    ]


    volumeAnswer = promptSecurely(volumeQuestion)
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

    finalConfirmation = promptSecurely(flashDriveQuestion)

    hl()
    if finalConfirmation['finalConfirmation']:
        print("Raspberry-Pack installation starts")
        os.system(cmdFormatDrive)

    else:
        print("❌ Raspberry-Pack installation was canceled. Nothing happened.")
        hl()
        sys.exit()


def waitForRaspberryToRespond():
    print("\n\n🥚 Waiting for the Raspberry-Pack to complete the installation\n(All in all this takes several minutes): ...\n")
    print("Soon you should see the live-feed from the Raspberry Pi's logs: (This can take more than 3 minutes)\n")
    cmdWaitForLiveLog = "nc -l 2000"

    # log injection phase
    print("Live: injection phase")
    os.system(cmdWaitForLiveLog)

    print("\nLive: installing phase (wait for reboot)")
    # log installation phase
    os.system(cmdWaitForLiveLog)


# reads the currents networks address and stores it into a file which will be pushed to the RPi
def setMasterIpFile():
    os.chdir(startLocation)
    os.chdir("packages/" + packageAnswer['package'] + "raspberry-pack/")

    stream = os.popen('ipconfig getifaddr en0')
    ipOfMaster = stream.read()

    ipFile = open('ip_of_master.conf', 'w+')
    ipFile.write(ipOfMaster)
    ipFile.truncate()
    ipFile.close()


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
    wifiAnswer = promptSecurely(wifiQuestion)

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
            'message': '🏷  What\'s the hostname for this Raspberry?',
            'default': hostname
        }
    ]
    hostnameAnswer = promptSecurely(hostnameQuestion)

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
            'message': '🔐 What\'s the password for this Raspberry?',
            'default': password
        }
    ]
    passwordAnswer = promptSecurely(passwordQuestion)

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

updatePackages()
hl()

[packageAnswer, packageShortName] = selectPackage()
enterPackageVariables()
hl()

setWiFiCredentials()
hl()

setHostname()

setPassword()
hl()

setMasterIpFile()

volumeAnswer = selectDisk()
hl()

flashDrive()
hl()

waitForRaspberryToRespond()
sys.exit()

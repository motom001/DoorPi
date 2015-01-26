#!/bin/bash
#
# DoorPI Setup Script
#

### CONFIG - START
InstallTo=/home/DoorPI
NeedPacks="wget git-core python2.7-dev python-daemon python-pifacedigitalio libv4l-dev libx264-dev libssl-dev libasound2-dev"
pjsip="http://www.pjsip.org/release/2.3/pjproject-2.3.tar.bz2"
VER='0.4.1'
### CONFIG - END

# internal variables
SystemUpgrade=0
FirmwareUpgrade=0
PackInstall=0
DoorPiInstall=0
[ -w '/usr/src' ] && SRC=/usr/src/ || SRC=/tmp/
[[ ${EUID} -ne 0 ]] && PFX='sudo ' || PFX=''

##- functions

_error() {
    if [ "$1" -gt 0 ]; then
        [ -z "$2" ] && message='' || message=" $2"
        echo "Es ist ein Fehler aufgetreten..$message"
        echo 'Abbruch'
        exit 1
    fi
}

function collectNeededPacks() {
    InstallPAK=""
    for PACK in $NeedPacks; do
        if [ -z "$(dpkg -l | grep "ii" | awk {'print $2'} | grep -xi $PACK)" ]; then
            [ -z "$InstallPAK" ] && InstallPAK="$PACK" || InstallPAK+=" $PACK"
        fi
        [ "$1" = "progress" ] && echo -n "."
    done
}

function welcome() {
    echo ""
    echo "DoorPI Setup Script (v${VER})"
    echo "==============================================================================="
    echo "Ziel des Projektes ist die Steuerung einer Türsprechanlage"
    echo "mittels einem Raspberry Pi (Model B) und PiFace."
    echo ""
    echo "DoorPi basiert auf dem Projekt 'door-berry' von 'mpodroid' (https://github.com/mpodroid/door-berry),"
    echo "aber seit einiger Zeit findet dort keine Entwicklung mehr statt."
    echo ""
    echo "-------------------------------------------------------------------------------"
    main_menu
}

function main_menu() {
    echo ""
    echo -en "\033[0;33m [O]S update | [P]akete installieren | [D]oorPI installieren | [R]eboot | [F]irmware update | []Beenden: \033[0m"
    echo ""
    read key
    case $key in
        [oO]) system_upgrade ;;
        [fF]) firmware_upgrade ;;
        [pP]) package_install ;;
        [dD]) doorpi_install ;;
        [rR]) sys_reboot ;;
        "") ;;
        *) echo -e "\033[1;31mUngueltige Eingabe!\033[0m"; main_menu ;;
    esac
}

function sys_reboot() {
    echo "Moechtest du jetzt wirklich rebooten? [y/n] "
    read key
    case $key in
        [yY][jJ]|[yY]es|[jJ]a) ${PFX}reboot ;;
        [nN]|[nN]o|[nN]ein) echo "Nein? Oke, schade..."; main_menu ;;
        *) echo "Nein? Oke, schade..."; main_menu ;;
    esac
}

function system_upgrade() {
    echo ""
    echo "* Update OS"
    ${PFX}apt-get update
    _error $?
    ${PFX}apt-get upgrade
    _error $?
    SystemUpgrade=1
    sleep 1
    main_menu
}

function firmware_upgrade() {
    echo ""
    echo -e "\033[1;31mACHTUNG:\033[0m Ein Firmware/Kernel-Update ueber 'rpi-update' sollte nur durchgefuehrt werden wenn man weiss was man tut!"
    echo "Die Firmware/Kernel ueber 'rpi-update' ist immer unstable."
    echo "Am 20.01.2015 wurde zudem auf den 'next' Kernel 3.18 gewechselt, wodurch sich einiges geaendert hat. Mehr dazu auf: https://github.com/raspberrypi/documentation/issues/150"
    echo "'rpi-update' sollte daher nur von erfahrenen Benutzern ausgefuehrt werden!"
    echo ""
    echo "Soll fortgefahren und rpi-update ausgefuehrt werden? [y/n] "
    read key
    case $key in
        [yY][jJ]|[yY]es|[jJ]a) sleep 1 ;;
        [nN]|[nN]o|[nN]ein) main_menu; return ;;
        *) main_menu; return ;;
    esac
    if [ -z "$(which rpi-update)" ]; then
        if [ -z "$(dpkg -l | grep "ii" | awk {'print $2'} | grep -xi 'git-core')" ]; then
             echo "Installiere benoetigtes Paket 'git-core'"
             apt-get install -y git-core
             echo ""
        fi
        echo "* Install rpi-update"
        ${PFX}wget http://goo.gl/1BOfJ -O /usr/bin/rpi-update
        _error $?
        ${PFX}chmod +x /usr/bin/rpi-update
    fi
    echo "* Update Firmware"
    ${PFX}rpi-update
    _error $?
    sleep 1
    if [ -f /boot/cmdline.txt ]; then
        if [ -z "$(grep 'dwc_otg.speed=1' /boot/cmdline.txt)" ]; then
            ${PFX}echo ' dwc_otg.speed=1' >> /boot/cmdline.txt
        fi
    else
        ${PFX}echo "dwc_otg.speed=1 dwc_otg.lpm_enable=0 console=ttyAMA0,115200 kgdboc=ttyAMA0,115200 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait" > /boot/cmdline.txt
    fi
    if [ ! -z "$(grep '^snd_bcm2835' /etc/modules)" ]; then
        echo "Entferne On-Board Sound Unterstuetzung"
        #grep -v 'snd_bcm2835' /etc/modules > /tmp/modules
        #sudo mv /tmp/modules /etc/
        ${PFX}sed -i /etc/modules -e "s/^snd_bcm2835.*/#snd_bcm2835/"
        ${PFX}modprobe -r snd_bcm2835
    fi
    if [ -f /etc/modprobe.d/raspi-blacklist.conf ] && [ -n "$(grep '^blacklist[[:space:]]*spi-bcm2708' /etc/modprobe.d/raspi-blacklist.conf)" ]; then
        echo "Binde SPI Unterstuetzung ein"
        ${PFX}sed -i /etc/modprobe.d/raspi-blacklist.conf -e "s/^blacklist[[:space:]]*spi-bcm2708.*/#blacklist spi-bcm2708/"
        ${PFX}modprobe spi-bcm2708
    fi
    FirmwareUpgrade=1
    main_menu
}

function package_install() {
    echo ""
    echo -n "Pruefe die von DoorPI benoetigten Pakete, bitte warten"
    collectNeededPacks "progress"
    if [ ! -z "$InstallPAK" ]; then
        apt-get install -y $InstallPAK
    else
        echo "Alle zur DoorPI installation benoetigten Pakete sind bereits installiert."
    fi
    if [ -z "$(find /usr/local/lib/python2.7/dist-packages/ -name pjsua.py)" ]; then
        rm -rf ${SRC}pjproject*
        echo -e "pjsip ist nicht installiert.. Lade herunter:\n"
        ${PFX}wget --progress=dot -P${SRC} $pjsip 2>&1 | grep --line-buffered '%' | sed -u -e 's,\.,,g' | awk '{printf("\b\b\b\b%4s", $2)}'
        echo -e "\nEntpacke, bitte warten."
        cd ${SRC}
        ${PFX}tar xfj $(basename $pjsip)
        _error $?
        cd pjproject-*
        echo "und kompilieren:"
        ./configure --disable-video --disable-l16-codec --disable-gsm-codec  --disable-g722-codec --disable-g7221-codec --disable-ilbc-codec
        _error $?
        ${PFX}echo '#   define PJMEDIA_AUDIO_DEV_HAS_ALSA       1' > pjlib/include/pj/config_site.h
        ${PFX}echo '#   define PJMEDIA_AUDIO_DEV_HAS_PORTAUDIO  0' >> pjlib/include/pj/config_site.h
        make dep && make && ${PFX}make install
        _error $?
        cd pjsip-apps/src/python
        make && ${PFX}make install
        _error $?
    fi
    sleep 1
    PackInstall=1
    main_menu
}

function doorpi_install() {
    echo ""
    local VALID=1
    if [ "$PackInstall" = 0 ]; then
        collectNeededPacks
        [ ! -z "$InstallPAK" ] && VALID=0
        [ -z "$(find /usr/local/lib/python2.7/dist-packages/ -name pjsua.py)" ] && VALID=0
        if [ "$VALID" = 0 ]; then
            echo "Zuerst muessen die benoetigten Pakete installiert werden!"
            package_install
        fi
    else
        echo "Installiere DoorPI, bitte warten."
        echo ""
        ${PFX}git clone https://github.com/motom001/DoorPi/ $InstallTo
        _error $?
        ${PFX}mkdir -p /var/log/doorpi/
        if [ ! -z "$(id pi 2>/dev/null)" ]; then
            ${PFX}chown -R pi:pi $InstallTo
            ${PFX}chown pi:pi /var/log/doorpi/
        fi
        ${PFX}sed -i "s|DOORPI_PATH=.*|DOORPI_PATH=$InstallTo|" $InstallTo/docs/service/doorpi
        ${PFX}sed -i "s|/home/pi/doorpi|$InstallTo|" $InstallTo/docs/service/doorpi
        ${PFX}chmod +x $InstallTo/docs/service/doorpi
        ${PFX}cp $InstallTo/docs/service/doorpi /etc/init.d/
        ${PFX}update-rc.d doorpi defaults
    fi
    DoorPiInstall=1
}

welcome

if [ "$DoorPiInstall" = 1 ]; then
    echo ""
    echo "Installation abgeschlossen"
    echo ""
fi

if [ "$FirmwareUpgrade" = 1 ]; then
    echo "Da die Firmware aktualisiert wurde ist ein reboot erforderlich! Jetzt rebooten? [y/n] "
    read key
    case $key in
        [yY][jJ]|[yY]es|[jJ]a) ${PFX}reboot ;;
        [nN]|[nN]o|[nN]ein) echo "Nein? Oke... Aber nicht vergessen!" ;;
        *) echo "Nein? Oke.. Aber nicht vergessen!" ;;
    esac
fi

exit 0

#!/bin/bash
#
# DoorPI Setup Script
#

### CONFIG - START
InstallTo=/home/DoorPI
LogDir=/var/log/doorpi
tmpfsDIR=/var/DoorPI
tmpfsDirSize=16M
NeedPacks="wget git-core python2.7-dev python-daemon libv4l-dev libx264-dev libssl-dev libasound2-dev"
pjsip="http://www.pjsip.org/release/2.3/pjproject-2.3.tar.bz2"
VER='0.7'
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
	echo "    ___                  ___ _"
	echo "   /   \___   ___  _ __ / _ (_)  DoorPI Setup Script (v${VER})"
	echo "  / /\ / _ \ / _ \| '__/ /_)/ |"
	echo " / /_// (_) | (_) | | / ___/| |"
	echo "/___,' \___/ \___/|_| \/    |_|"
	echo ""
	echo "==============================================================================="
	echo "Ziel des Projektes ist die Steuerung einer Tuersprechanlage"
	echo "mittels einem Minicomputer wie Raspberry Pi und PiFace."
	echo ""
	echo "DoorPi basiert auf dem Projekt 'door-berry' von 'mpodroid'"
	echo "und ist unter der URL https://github.com/motom001/DoorPi zu finden"
	echo ""
	echo "-------------------------------------------------------------------------------"
	main_menu
}

function main_menu() {
	echo ""
	echo -en "\033[0;33m [O]S Menue | [A]bhaengigkeiten Menue | [D]oorPI installieren | [R]eboot | []Beenden: \033[0m"
	echo ""
	read key
	case $key in
		[oO]) system_preparation_menu ;;
		[aA]) dependencies_menu ;;
		[dD]) doorpi_install ;;
		[rR]) sys_reboot ;;
		"") ;;
		*) echo -e "\033[1;31mUngueltige Eingabe!\033[0m"; main_menu ;;
	esac
}

function system_preparation_menu() {
	echo ""
	echo -en "\033[0;33m [O]S update | [F]irmware update | [R]eboot | []Zurueck zum Hauptmenue: \033[0m"
	echo ""
	read key
	case $key in
		[oO]) system_upgrade ;;
		[fF]) firmware_upgrade ;;
		[rR]) sys_reboot ;;
		""]) main_menu ;;
		*) echo -e "\033[1;31mUngueltige Eingabe!\033[0m"; system_preparation_menu ;;
    esac
}

function dependencies_menu() {
	echo ""
	LINE="[A]bhaengigkeiten installieren"
	[ ! -z "$tmpfsDIR" ] && LINE+=" | [T]mpfs installieren"
	LINE+=" | [P]iface installieren | []Zurueck zum Hauptmenue"
	echo -en "\033[0;33m $LINE: \033[0m"
	echo ""
	read key
	case $key in
		[aA]) package_install ;;
		[pP]) doorpi_install_piface ;;
		[tT]) doorpi_install_tmpfs ;;
		"") main_menu ;;
		*) echo -e "\033[1;31mUngueltige Eingabe!\033[0m"; dependencies_menu ;;
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

function doorpi_install_tmpfs() {
	echo ""
	if [ ! -z "$tmpfsDIR" ]; then
		echo "Richte tmpfs Verzeichnis $tmpfsDIR fuer DoorPi ein"
		if [ ! -z "$(grep -i "tmpfs.*$tmpfsDIR" /etc/fstab)" ]; then
			echo "tmpfs ist in /etc/fstab schon fuer $tmpfsDIR vorhanden."
		else
			${PFX}echo "tmpfs        $tmpfsDIR        tmpfs    size=$tmpfsDirSize    0    0" >> /etc/fstab
		fi
		[ ! -d $tmpfsDIR ] && ${PFX}mkdir -p $tmpfsDIR
		echo "Mount tmpfs.."
		${PFX}mount -a
	else
		echo -e "\033[1;31mFehler: Die Script-Einstellung tmpfsDIR fehlt! Tmpfs-Installation kann nicht ausgefuehrt werden!\033[0m"
	fi
	main_menu
}

function doorpi_install_piface() {
	echo ""
	PiFacePack='python-pifacedigitalio'
	echo "Pruefe die fuers PiFace benoetigte Paket, bitte warten."
	if [ -z "$(dpkg -l | grep "ii" | awk {'print $2'} | grep -xi $PiFacePack)" ]; then
		echo "Installiere $PiFacePack:"
		apt-get install -y $PiFacePack
	else
		echo "Alle fuer PiFace benoetigten Pakete sind bereits installiert."
	fi
	if [ -f /etc/modprobe.d/raspi-blacklist.conf ] && [ -n "$(grep '^blacklist[[:space:]]*spi-bcm2708' /etc/modprobe.d/raspi-blacklist.conf)" ]; then
		echo ""
		echo "Binde SPI Unterstuetzung ein"
		${PFX}sed -i /etc/modprobe.d/raspi-blacklist.conf -e "s/^blacklist[[:space:]]*spi-bcm2708.*/#blacklist spi-bcm2708/"
		${PFX}modprobe spi-bcm2708
	fi
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
		${PFX}mkdir -p $LogDir
		if [ ! -z "$(id pi 2>/dev/null)" ]; then
			${PFX}chown -R pi:pi $InstallTo
			${PFX}chown pi:pi $LogDir
		fi
		${PFX}sed -i "s|DOORPI_PATH=.*|DOORPI_PATH=$InstallTo|" $InstallTo/docs/service/doorpi
		${PFX}sed -i "s|/home/pi/doorpi|$InstallTo|" $InstallTo/docs/service/doorpi
		${PFX}chmod +x $InstallTo/docs/service/doorpi
		${PFX}cp $InstallTo/docs/service/doorpi /etc/init.d/
		${PFX}update-rc.d doorpi defaults
		doorpi_install_tmpfs
		if [ -f /boot/cmdline.txt ]; then
			if [ -z "$(grep 'dwc_otg.speed=1' /boot/cmdline.txt)" ]; then
				echo "Erweitere /boot/cmdline.txt um den 'dwc_otg.speed=1' Eintrag"
				${PFX}sed -i /boot/cmdline.txt -e 's/^/dwc_otg.speed=1 /'
			fi
		else
			echo "Erstelle /boot/cmdline.txt , da nicht vorhanden"
			${PFX}echo "dwc_otg.speed=1 dwc_otg.lpm_enable=0 console=ttyAMA0,115200 kgdboc=ttyAMA0,115200 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait" > /boot/cmdline.txt
		fi
		if [ ! -z "$(grep '^snd_bcm2835' /etc/modules)" ]; then
			echo "Entferne On-Board Sound Unterstuetzung"
			${PFX}sed -i /etc/modules -e "s/^snd_bcm2835.*/#snd_bcm2835/"
			${PFX}modprobe -r snd_bcm2835
		fi
	fi
	DoorPiInstall=1
	main_menu
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
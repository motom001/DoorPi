#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from time import sleep
import subprocess
import urllib2
import json

import metadata

SETUP_VERSION = 0.1
NEEDED_PACKEGES_APTGET = ['python-pip']
NEEDED_PACKEGES_PIP = []

NEEDED_TMPFS_PATH = "/var/DoorPi"
NEEDED_TMPFS_SIZE = "16M"

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

'''
watchdog
RPi.GPIO
pifacedigitalio // pifacecommon

wheel
linphone4raspberry
'''
class Entry:
    pass

class Environment:
    @property
    def is_win(self):
        try: return "WINDOWS" in self.system.os
        except : return False

    @property
    def is_unix(self):
        try: return "UNIX" in self.system.os
        except: return False

    def __init__(self):
        self.setup = Entry()
        self.system = Entry()
        self.requirements = Entry()

        self.keyboard = Entry()
        self.sipphone = Entry()

        self.doorpi = Entry()

        try:
            response = urllib2.urlopen('https://raw.githubusercontent.com/motom001/DoorPi/Installer/.version').read()
            self.remote_version_file = json.loads(response)
        except:
            self.remote_version_file = None

    def refresh_status(self):
        self.collect_status_system()
        self.collect_status_setup()
        self.collect_status_keyboard()
        self.collect_status_sipphone()
        self.collect_status_doorpi()

    def collect_status_system(self):
        self.system.os = "UNIX"

        self.system.tmpfs = Entry()
        result = subprocess.Popen(
            "grep -i 'tmpfs.*doorpi' /etc/fstab | awk {'print $2'}",
            shell = True,
            stdout = subprocess.PIPE
        ).stdout.read()
        if result:
            self.system.tmpfs.active = True
            self.system.tmpfs.path = result[:-1]
            result = subprocess.Popen(
                "grep -i 'tmpfs.*doorpi' /etc/fstab | awk {'print $4'}",
                shell = True,
                stdout = subprocess.PIPE
            ).stdout.read()
            self.system.tmpfs.size = result[5:-1]
        else:
            self.system.tmpfs.active = False
            self.system.tmpfs.path = ""
            self.system.tmpfs.size = "0M"

        result = subprocess.Popen(
            "grep '^snd.bcm2835' /etc/modules",
            shell = True,
            stdout = subprocess.PIPE
        ).stdout.read()
        self.system.OnboardSound = True if result else False

        self.system.aptget = Entry()
        self.system.aptget.missing = NEEDED_PACKEGES_APTGET
        self.system.aptget.installed = []
        for Package in self.system.aptget.missing:
            version = subprocess.Popen(
                "dpkg -l | grep '"+Package+"' | grep 'ii' | awk {'print $3'}",
                shell = True,
                stdout = subprocess.PIPE
            ).stdout.read()
            if version:
                self.system.aptget.installed.append(Package+' in version '+version[:-1])
                self.system.aptget.missing.remove(Package)

        self.system.pip = Entry()
        self.system.pip.missing = NEEDED_PACKEGES_PIP
        self.system.pip.installed = []
        for Package in self.system.pip.missing:
            version = subprocess.Popen(
                "pip freeze | grep '"+Package+"'",
                shell = True,
                stdout = subprocess.PIPE
            ).stdout.read()
            if version:
                if "===" in version:
                    self.system.pip.installed.append(Package+' in version '+version[version.find('===')+3:-1]+" installed manuelly")
                elif "==" in version:
                    self.system.pip.installed.append(Package+' in version '+version[version.find('==')+2:-2]+" installed with repository")
                self.system.pip.missing.remove(Package)



    def collect_status_setup(self):
        self.setup.url = self.remote_version_file['setup_script_url']
        self.setup.version_local = SETUP_VERSION
        self.setup.version_remote = self.remote_version_file['setup_script_version']

    def collect_status_keyboard(self):
        pass

    def collect_status_sipphone(self):
        self.sipphone.linphone = Entry()
        result = subprocess.Popen(
            "find /usr/local/lib -name 'linphone4raspberry-*.dist-info'",
            shell = True,
            stdout = subprocess.PIPE
        ).stdout.read()
        if result:
            self.sipphone.linphone.installed = True
            start_id = result.find('linphone4raspberry-') + len('linphone4raspberry-')
            self.sipphone.linphone.version = result[start_id:-len('.dist-info')-1]
        else:
            self.sipphone.linphone.installed = False
            self.sipphone.linphone.version = ""

        self.sipphone.pjsua = Entry()
        result = subprocess.Popen(
            "find /usr/local/lib -name 'pjsua-*.egg-info'",
            shell = True,
            stdout = subprocess.PIPE
        ).stdout.read()
        if result:
            self.sipphone.pjsua.installed = True
            start_id = result.find('pjsua-') + len('pjsua-')
            self.sipphone.pjsua.version = result[start_id:-len('.egg-info')-1]
        else:
            self.sipphone.pjsua.installed = False
            self.sipphone.pjsua.version = ""

    def collect_status_doorpi(self):
        pass

class SetupClass:

    def __init__(self):
        self.OS_VERSION = ""
        self.environment = Environment()
        self.exit = -1
        self.last_message = ""

    def do_self_update(self):
        update_file = BASE_PATH+"/setup_update.py"
        fo = open(update_file, "w")
        fo.write(
            '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess, urllib2, os, sys
setup_file = "{base_path}/setup2.py"
response = urllib2.urlopen('{setup_script_url}').read()
fo = open(setup_file, "w")
fo.write(response)
fo.close()
os.chmod(setup_file, 0o777)
#os.execv(setup_file, sys.argv)'''.format(
                setup_script_url = self.environment.setup.url,
                base_path = BASE_PATH
            )
        )
        fo.close()
        os.chmod(update_file, 0o777)
        os.execv(update_file, sys.argv)

    def run(self):
        self.refresh_environment()
        if self.environment.is_unix: self.check_root()

        if self.environment.setup.version_remote > self.environment.setup.version_local:
            info = "Das Setup-Script ist veraltet und sollte aktuallisiert werden!\n"
            info += "Soll dieses Update jetzt automatisch durchgeführt werden?\n"
            info += "neuste Version %s - lokale Version %s"%(self.environment.setup.version_remote, self.environment.setup.version_local)
            question = "Ja, bitte durchführen"
            if self.ask_menu(info, question) is True:
                self.do_self_update()
                raise SystemExit(1)
            else:
                self.last_message = "Das Setup-Script ist veraltet und sollte aktuallisiert werden!"

        self.last_message += "\nInstaller befindet sich im Beta-Status und ist nicht funktionsfähig!"
        while self.exit == -1:
            try:
                self.main_menu()
            except Exception as exp:
                self.last_message = str(exp)
        self.base_menu()
        raise SystemExit(self.exit)

    def clear_screen(self):
        if self.environment.is_win: os.system("cls")
        if self.environment.is_unix: os.system("clear")

    def back_last_menu(self, *args):
        self.exit = 0

    def exit_setup(self):
        self.last_message = "DoorPi-Setup wird nun beendet"
        self.exit = 0

    def check_root(self):
        if os.geteuid() != 0:
            self.last_message = "ERROR: DoorPi-Setup must run with sudo rights"
            print(self.last_message)
            self.exit = 1

    def base_menu(self, header = ""):
        self.clear_screen()
        print(metadata.epilog)
        print("")
        if len(self.last_message):
            print("==================================================================================")
            print(self.last_message)
        if len(header):
            print("==================================================================================")
            print(header)
        print("==================================================================================")

    def folgemenu(self, *args, **kwargs):
        print "tu es"
        sleep(1.5)
        print "fertig"
        self.ask_menu(
            info = 'Das ist ein text \n über mehrere Zeilen',
            question = 'War das erfolgreich?'
        )
        self.exit = 0

    def main_menu(self):
        self.base_menu()
        menue_structure = {
            "0": self.exit_setup,
            "10": self.folgemenu,
            "20": self.sipphones_menu,
            "30": self.requirements_menu,
            "40": self.folgemenu
        }
        print("| 10) Keyboards                                   %s"%self.keyboards_check())
        print("| 20) SIP-Phones                                  %s"%self.sipphones_check('*'))
        print("| 30) Voraussetzungen                             %s"%self.requirements_check('*'))
        print("| 40) DoorPi                                      %s"%self.doorpi_check())
        print("|")
        print("| 0) Exit")
        print("==================================================================================")
        choice = raw_input("Auswahl [0]: ") or "0"
        while self.exit == -1:
            menue_structure[choice]()
        if choice is not "0": self.exit = -1

    def ask_menu(self, info, question):
        self.base_menu()
        print(info)
        print("==================================================================================")
        choice = raw_input(question+" [y]: ") or "y"
        return choice in ['y', 'Y', 'j', 'J', '1']

    def execute_with_live_preview_and_menu(self, header, cmd):
        self.base_menu()
        print("| "+header)
        print("==================================================================================")
        self.execute_with_live_preview(cmd)

    @staticmethod
    def execute_with_live_preview(cmd):
        sub_process = subprocess.Popen(
            cmd,
            shell = True,
            stderr = subprocess.STDOUT,
            stdout = subprocess.PIPE
        )
        while sub_process.poll() is None:
            out = sub_process.stdout.read(1)
            sys.stdout.write(out)
            sys.stdout.flush()

    def refresh_environment(self, *args):
        self.base_menu("Erfasse Systemumgebung - bitte warten...")
        self.environment.refresh_status()

    def keyboards_check(self):
        return "[linphone]"

    def doorpi_check(self):
        return "[Update nötig (von 2.1 auf 2.45)]"

    def sipphones_check(self, part):
        return_string = []
        if not self.environment.sipphone.linphone.installed and not self.environment.sipphone.pjsua.installed:
            return_string.append('kein sipphone installiert')
        else:
            if part == "linphone":
                if self.environment.sipphone.linphone.installed:
                    return_string.append('installiert')
                else:
                    return_string.append('nicht installiert')
            elif part == "pjsua":
                if self.environment.sipphone.pjsua.installed:
                    return_string.append('installiert')
                else:
                    return_string.append('nicht installiert')

        if part == "*":
            return "[check]" if len(return_string) == 0 else "[%s Fehler]"%len(return_string)
        else:
            return "[check]" if len(return_string) == 0 else "%s"%return_string

    def sipphones_do(self, part):
        if part == "linphone":
            if self.environment.sipphone.linphone.installed:
                self.last_message = "linphone ist bereits installiert"
                return False

        if part == "pjsua":
            return False

        self.refresh_environment()
        return True

    def sipphones_menu(self):
        self.base_menu("bitte mindestens ein Sip-Phone auswählen")
        menue_structure = {
            "0": self.back_last_menu,
            "1": self.sipphones_do,
            "2": self.sipphones_do
        }
        print("| 1) linphone installieren                       %s"%self.sipphones_check('linphone'))
        print("| 2) pjsua installieren                          %s"%self.sipphones_check('pjsua'))
        print("|")
        print("| 0) zurück")
        print("==================================================================================")
        choice = raw_input("Auswahl [0]: ") or "0"
        menue_structure[choice](choice)

    def requirements_check(self, part):
        return_string = []

        if part == "apt-get" or part == "*":
            if len(self.environment.system.aptget.missing):
                return_string.append('fehlende %s Pakete bei apt-get'%len(self.environment.system.aptget.missing))

        if part == "pip" or part == "*":
            if "python-pip" in self.environment.system.aptget.missing:
                return_string.append('python-pip ist nicht installiert')
            elif len(self.environment.system.pip.missing):
                return_string.append('fehlende %s Pakete bei pip'%len(self.environment.system.pip.missing))

        if part == "tmpfs" or part == "*":
            if not self.environment.system.tmpfs.active:
                return_string.append('kein tmpfs fuer DoorPi eingerichtet')
            elif self.environment.system.tmpfs.path != NEEDED_TMPFS_PATH:
                return_string.append('falscher tmpfs Pfad ('+self.environment.system.tmpfs.path+' statt '+NEEDED_TMPFS_PATH+')')
            elif self.environment.system.tmpfs.size != NEEDED_TMPFS_SIZE:
                return_string.append('falscher tmpfs Groesse ('+self.environment.system.tmpfs.size+' statt '+NEEDED_TMPFS_SIZE+')')

        if part == "OnboardSound":
            if self.environment.system.OnboardSound:
                return_string.append("OnboardSoundCard ist noch aktiviert")

        if part == "system_update" or part == "*":
            pass

        if part == "firmware_update" or part == "*":
            pass

        if part == "*":
            return "[check]" if len(return_string) == 0 else "[%s Fehler]"%len(return_string)
        else:
            return "[check]" if len(return_string) == 0 else "%s"%return_string

    def requirements_do(self, part):
        if part == "apt-get" or part == "1":
            if not len(self.environment.system.aptget.missing):
                self.last_message = "Ausführung von apt-get abgebrochen - alle Bedingungen sind bereits erfüllt"
                return False
            self.execute_with_live_preview_and_menu(
                'führe "apt-get update" aus um die Paketliste auf den neusten Stand zu bekommen:',
                'apt-get update'
            )
            info = 'Sollen die folgenden apt-get Pakete installiert werden?\n'
            info += '\n'.join(self.environment.system.aptget.missing)
            question = 'Ja, bitte ausführen'
            if self.ask_menu(info, question) is True:
                command_line = "apt-get install -y "+' '.join(self.environment.system.aptget.missing)
                self.execute_with_live_preview_and_menu("Ausführung von: '%s'"%command_line, command_line)
            else:
                self.last_message = "Ausführung von apt-get abgebrochen"
                return False

        if part == "pip" or part == "2":
            if "python-pip" in self.environment.system.aptget.missing:
                self.last_message = "Ausführung von pip abgebrochen - pip ist nicht installiert"
                return False
            if not len(self.environment.system.pip.missing):
                self.last_message = "Ausführung von pip abgebrochen - alle Bedingungen sind bereits erfüllt"
                return False
            info = 'Sollen die folgenden pip Pakete installiert werden?\n'
            info += '\n'.join(self.environment.system.pip.missing)
            question = 'Ja, bitte ausführen'
            if self.ask_menu(info, question) is True:
                command_line = "pip install "+' '.join(self.environment.system.aptget.missing)
                self.execute_with_live_preview_and_menu("Ausführung von: '%s'"%command_line, command_line)
            else:
                self.last_message = "Ausführung von pip abgebrochen"
                return False

        if part == "tmpfs" or part == "3":
            if not len(self.requirements_check('tmpfs')):
                self.last_message = "tmpfs ist bereits korrekt eingerichtet"
                return False
            if self.environment.system.tmpfs.active:
                info = 'Es wurde bereits ein tmpfs in der Datei /etc/fstab eingerichtet\n'
                info += 'hat aber entweder eine falsche Größe oder einen falschen Pfad.\n'
                info += 'Soll die bestehende Konfiguration aus /etc/fstab gelöscht werden (nicht empfohlen)?'
                question = 'Ja, bitte ausführen'
                if self.ask_menu(info, question) is True:
                    self.last_message = "Das automatische Editieren der fstab wurde aus Sicherheitsgründen deaktiviert!"
                    return False

            new_fstab = 'tmpfs        '+NEEDED_TMPFS_PATH+'        tmpfs    size='+NEEDED_TMPFS_SIZE+'    0    0'
            info = 'Soll ein tmpfs in der Datei /etc/fstab eingetragen werden?\n'
            info += 'Hinzugefügt wird:\n'
            info += '"'+new_fstab+'"'
            info += 'danach wird das Verzeichnis "'+NEEDED_TMPFS_PATH+'" erstellt und "mount -a" ausgeführt'
            question = 'Ja, bitte ausführen'
            if self.ask_menu(info, question) is True:
                command_line = "echo "+new_fstab+" >> /etc/fstab && mkdir -p "+NEEDED_TMPFS_PATH#+" && mount -a"
                self.execute_with_live_preview_and_menu("Ausführung von: '%s'"%command_line, command_line)

        if part == "OnboardSound" or part == "10":
            if not self.environment.system.OnboardSound:
                self.last_message = "OnboardSoundCard ist bereits deaktiviert"
                return False
            info = 'Soll in der Datei /etc/modules der OnboardSound (snd-bcm2835) deaktiviert\n'
            info += 'und danach das Modul mit modprobe entladen werden?'
            question = 'Ja, bitte ausführen'
            if self.ask_menu(info, question) is True:
                command_line = 'sudo sed -i /etc/modules -e "s/^snd.bcm2835.*/#snd-bcm2835/"'
                command_line += ' && modprobe -r snd_bcm2835'
                self.execute_with_live_preview_and_menu("Ausführung von: '%s'"%command_line, command_line)
            else:
                self.last_message = "Ausführung von OnboardSound abgebrochen"
                return False

        if part == "system_update" or part == "20":
            self.execute_with_live_preview_and_menu(
                'führe "apt-get update" aus um die Paketliste auf den neusten Stand zu bekommen:',
                'apt-get update'
            )
            info = 'Soll wirklich eine System-Aktuallisierung durchgeführt werden?\n'
            info += 'apt-get upgrade -y && apt-get dist-upgrade -y'
            question = 'Ja, bitte ausführen'
            if self.ask_menu(info, question) is True:
                command_line = "apt-get upgrade -y && apt-get dist-upgrade -y"
                self.execute_with_live_preview_and_menu("Ausführung von: '%s'"%command_line, command_line)
            else:
                self.last_message = "Ausführung von System-Update abgebrochen"
                return False

        if part == "firmware_update" or part == "21":
            self.last_message = "Firmware-Update ist noch nicht implementiert :P\n"
            self.last_message += "http://raspberrypiguide.de/howtos/raspberry-pi-firmware-update/"
            return False

        self.refresh_environment()
        return True

    def requirements_menu(self):
        self.base_menu()
        menue_structure = {
            "0": self.back_last_menu,
            "1": self.requirements_do,
            "2": self.requirements_do,
            "3": self.requirements_do,
            "10": self.requirements_do,
            "20": self.requirements_do,
            "21": self.requirements_do,
            "30": self.refresh_environment
        }
        print("| erforderlich: ")
        print("| 1) apt-get Pakete                              %s"%self.requirements_check('apt-get'))
        print("| 2) pip-Pakete                                  %s"%self.requirements_check('pip'))
        print("| 3) temp. Ordner (tmpfs)                        %s"%self.requirements_check('tmpfs'))
        print("|")
        print("| optional: ")
        print("| 10) OnBoard-Sound deaktivieren                 %s"%self.requirements_check('OnboardSound'))
        print("| 20) System-Update                              ")
        print("| 21) Firmware-Update                            ")
        print("| 30) Systemumgebung erneut einlesen             ")
        print("|")
        print("| 0) zurück")
        print("==================================================================================")
        choice = raw_input("Auswahl [0]: ") or "0"
        menue_structure[choice](choice)

if __name__ == '__main__':
    setup_object = SetupClass()
    setup_object.run()

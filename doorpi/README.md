
Achtung: Aktuell gibt es Probleme beim Transfer von github Repository zu einem pypi Paket.

Attention: At the moment I have problems to convert my github project to a running pypi module.


[DE]
==========

Ziel des Projektes DoorPi ist die Steuerung einer Türsprechanlage mittels einem Einplatiniencomputer wie dem Raspberry Pi.

Dazu sollen Ereignisse (Events) wie "Drücken einer Türklingel" oder "NFC Chip xyz vorgehalten" die Auslöser von Aktionen (Actions) wie "Anruf bei Telefon xyz" oder "E-Mail an xxx"  sein.

Um diese Events zu registrieren werden "DoorPi-Keyboards" genutzt, was z.B. 
* die GPIO-Pins
* ein PiFace 
* Dateien im Dateisystem des Pi (z.B. für Remote-Befehle über SSH)
* die serielle Schnittstelle (RDM6300 als NFC Reader)
* Webservice mit Authentifizierung
* VoIP-Telefon
sein können.

An jedes Event können beliebig viele Actions angefügt werden, die syncron oder asyncron ausgeführt werden. Eine nicht vollständige Liste der Actions ist:
* VoIP Anruf zu festgelegter Nummer starten
* VoIP Anruf zu Nummer starten, die aus einer Datei ausgelesen wird
* Anruf beenden
* E-Mail versenden
* Programm ausführen
* Ausgang schalten
* Status-Datei schreiben
* Werte aus IP-Symcon lesen oder zurück schreiben
* ...
Durch die Kombination der Events und Actions sind fast alle gewünschten Kombinationen möglich. 

Ein mögliches Szenario ist:
1. Beim Druck eines Klingeltasters wird ein Anruf ausgelöst und gezielt eine Nummer angerufen (z.B. interne FritzBox Nummer **613 aber auch Handynummern).
2. Der Bewohner kann mit der Außenstelle telefonieren und auf Wunsch die Tür remote öffnen, in dem eine definierte Taste (oder Tastenfolge) auf dem Telefon gedrückt wird.
3. Der Bewohner vergisst das auflegen und DoorPi beendet selbst das Gespräch, sobald die Tür wieder geschlossen wurde.
4. DoorPi versendet eine E-Mail, dass es einen Anruf gab, jemand die Tür geöffnet hat und jemand ins Haus gegangen ist.

Mittlerweile gibt es auch Video-Support, so dass an der Haustür eine Kamera installiert werden kann und das Bild auf den Innenstationen angesehen werden kann, noch bevor das Gespräch angenommen wird.

Weitere Informationen zur Installation und Konfiguration von DoorPi sind im Wiki unter https://github.com/motom001/DoorPi/wiki zu finden.

*Link zu Foren mit DoorPi Threads:*

* http://www.forum-raspberrypi.de/Thread-haussteuerung-doorpi-voip-wechselsprechanlage-tuersprechanlage
* http://www.ip-symcon.de/forum/threads/26739-DoorPI-VoIP-Door-Intercomstation-with-Raspberry-Pi
* http://raspberrycenter.de/forum/doorpi-voip-wechselsprechanlage-tuersprechanlage
* http://forum.lemaker.org/thread-11817-1-1-_pass_doorpi_voip_door_intercomstation_with_bananapi.html


[EN]
==========

The aim of the project is to connect the intercom with mini-computer and a optional PiFace or GPIO with a relais. 
On github I found something similar, the project “door-berry” from “mpodroid” (https://github.com/mpodroid/door-berry).
There hasn't been any development for a long time and there was still a lot to do, but it was perfect as a template.

DoorPi aims to be a cheap alternative to install a doorcom, instead of expensive commercial products.
With DoorPi all phones ring if someone rings the bell and you can communicate with the people outside.

Requirements:
* Raspberry Pi with installed Raspbian OS
* optional PiFace
* Soundcard
* SD card

Possibilities with DoorPi
* Connection to an existing intercom (e.g. 3 push-buttons, microphone, speaker)
* Triggering diffent actors (like door opener, light) by pushing a button on the phone (e.g. #)
* Communication with an existing VoIP-server (e.g. FritzBox, Asterisk)
* every push-button should dial a different phone number

The connection to the different actors can be realised with PiFace or a relais connected to the GPIOs.

You can install the project with the DoorPi.sh script (http://raspberrypi.roxxs.org/EPSPi/packs/DoorPI.sh)

You can find further information for installation and configuration in the DoorPi wiki: https://github.com/motom001/DoorPi/wiki

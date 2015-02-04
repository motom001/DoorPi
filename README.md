[DE]
==========
Ziel des Projektes ist die Steuerung einer Türsprechanlage mittels einem Minicomputer wie dem Raspberry Pi und optional PiFace / GPIO.
Dazu habe ich das Projekt "door-berry" von "mpodroid" auf github gefunden (https://github.com/mpodroid/door-berry). 
Seit einiger Zeit findet dort aber keine Entwicklung mehr statt und es ist dort noch recht viel zu tun. Aber als Vorlage war es perfekt.

Mit Hilfe von DoorPi soll die Möglichkeit bestehen, eine im Vergleich zu kommerziellen Produkten, günstige Variante einer Sprechanlage zu realisieren. Dabei sollen beim Klingeln die im Haus vorhandenen Telefon oder auch externe Nummer angerufen werden, über die dann mit der an der Tür stehenden Person kommuniziert werden kann.

Vorraussetzungen:
* Raspberry Pi mit installiertem Raspbian OS
* optional PiFace
* Soundkarte
* SD-Karte

Möglichkeiten mit DoorPi
* Anschluss der vorhanden Türsprechanlage (Bsp. 3 Taster, Mikrofon, Lautsprecher)
* Ansteuerung des verschiedener Aktoren (wie Türöffner, Licht) per Tastendruck am Telefon (z.B. #)
* Kommunikation mittels VoIP mit einem VoIP Server (z.B. FritzBox, Asterix)
* pro Klingel-Taste soll eine andere Rufnummer gewählt werden (können)

Der Anschluss der einzelnen Aktoren kann mit einem PiFace oder per GPIO und einem Relais realisiert werde. 

Die Installation wird mittels des DoorPI.sh (http://raspberrypi.roxxs.org/EPSPi/packs/DoorPI.sh) Skripts durchgeführt.

Weiter Informationen zur Installation und Konfiguration von DoorPi sind im Wiki unter https://github.com/motom001/DoorPi/wiki zu finden.

[EN]
==========

The aim of the project is to connect the intercom with mini-computer and a optional PiFace or GPIO with a relais. 
On github I found something similar, the project “door-berry” of “mpodroid” (https://github.com/mpodroid/door-berry).
There isn't any development since a long time and there was still a lot to do, but it was perfect as template.

DoorPi should be a cheap alternative to install a doorcom, instead of expensive commercial products.
With DoorPi all phones should ring if someone rings the bell and you can communicate with the people outside.

Requirements:
* Raspberry Pi with installed Raspbian OS
* optional PiFace
* Soundcard
* SD card

Possibilities with DoorPi
* Connection to an existing intercom (e.g. 3 push-buttons, microphone, speaker)
* Triggering diffent actos  (like door opener, light) by pushing a button on the phone (e.g. #)
* Kommunikation mittels VoIP mit einem VoIP Server (z.B. FritzBox, Asterix)
* every push-button should dial a different phone number

The connection to the different actors should be realised by PiFace or a relais connected to the GPIOs.

You can install the project with the DoorPi.sh script (http://raspberrypi.roxxs.org/EPSPi/packs/DoorPI.sh)

You can find further information for installation and cnofiguration in the DoorPi wiki: https://github.com/motom001/DoorPi/wiki

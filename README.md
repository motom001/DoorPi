

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

The aim of the project is to connect the intercom with a RaspberryPi (model B) and PiFace. On github I found something similar, the project “door-berry” of “mpodroid” (https://github.com/mpodroid/door-berry).

Intercom Requirements:

Service:
-	24/7 at the hall
-	stable

Gateway Input
-	Connection to an existent intercom (3 push-buttons, microphone, speaker)
-	Piloting the door opener (12V DC) by pressing a key at the phone (e.g. #)

Gateway Output:
-	Communication via VoIP (AVM Fritz!Box 7490 as VoIP-Server)
-	every push-button should dial a different phone number

My composition:
-	house with 3 floors – a hirer per floor 
-	all hirer share one internet and phone mainline
-	Fritz!Box 7490 at second floor
  o	Works as Router, Switch, DECT-base and Wi-Fi Access-Point
  o	Even as VoIP-Server (http://en.avm.de/nc/service/fritzbox/fritzbox-7490/knowledge-base/publication/show/42/)
-	First floor: Fritz!Powerline 546E Powerline-adapter as Wi-Fi Access-Point (connected by patch-cable)
-	Ground: Fritz!Box 7270
  o	Works as Switch, DECT-base, Wi-Fi Access-Point
  o	Even as power-connection for the RaspberryPi
  o	Replaced Fritz!Box power supply (12 DC, 2,5A)
  o	Power cord split to 7270, relais of PiFace for door opener and lightning of intercom
-	RaspberryPi (model B) with PiFace in a large case
-	USB-soundcard (http://www.conrad.de/ce/de/product/872300)

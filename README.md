

[DE]
==========
Da mein Englisch nicht immer das Beste ist, starte ich die Beschreibung in Deutsch und hoffe auf Hilfe bei der Übersetzung.
Ziel des Projektes ist die Steuerung einer Türsprechanlage mittels einem Raspberry Pi (Model B) und PiFace. 
Dazu habe ich das Projekt "door-berry" von "mpodroid" auf github gefunden (https://github.com/mpodroid/door-berry). 
Seit einiger Zeit findet dort aber keine Entwicklung mehr statt und es ist dort noch recht viel zu tun. Aber als Vorlage war es perfekt.


Anforderungen an meine Türsprechanlage:

Betrieb:
* 24/7 im Hausflur
* stabil

Schnittstellen Input:
* Anschluss der vorhanden Türsprechanlage (3 Taster, Mikrofon, Lautsprecher)
* Ansteuerung des Türöffners (12V DC) per Tastendruck am Telefon (z.B. #)

Schnittstellen Output:
* Kommunikation mittels VoIP (VoIP-Server ist eine AVM FRITZ!BOS 7490)
* pro Klingel-Taste soll eine andere Rufnummer gewählt werden (können)


Der Aufbau bei mir ist:
* Haus mit 3 Etagen - pro Etage ein eigener Mieter
* alle Mieter teilen sich eine DSL und Telefonanschluss
* im 2. OG: FRITZ!BOS 7490
- als DSL-Router, Netzwerk-Switch, DECT-Basis, WLAN-Access-Point
- sowie als VoIP-Server (http://avm.de/nc/service/fritzbox/fritzbox-7490/wissensdatenbank/publication/show/42_IP-Telefon-an-FRITZ-Box-anmelden-und-einrichten/)
* im 1. OG: FRITZ!Powerline 546E Powerline-Adapter als WLAN-Access-Point (per Netzwerkkabel angeschlossen)
* im EG: FRITZ!BOX 7270
- als Netzwerk-Switch, DECT-Basis, WLAN-Access-Point
- sowie als Stromversorger für Raspberry Pi
- Netzteil der FritzBox ersetzt gegen ein stärkeres (12 DC, 2,5A)
- Netzkabel gesplittet - einmal für die 7270, einmal an die Relais vom PiFace für den Türöffner sowie Beleuchtung Türsprechanalage
* Raspberry PI (Model B) mit PiFace im großzügigen Gehäuse
* USB-Soundkarte EAN: 4016138697902 (http://www.conrad.de/ce/de/product/872300)

[EN]
==========

coming soon
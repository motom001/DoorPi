****************************************************
DoorPi: OpenSource VoIP Door-Intercomstation
****************************************************

.. _VoIP: https://de.wikipedia.org/wiki/IP-Telefonie
.. _PyPi: https://pypi.python.org/pypi/DoorPi
.. _GitHub: https://github.com/motom001/DoorPi

.. |travis_status_master| image:: https://travis-ci.org/motom001/DoorPi.svg?branch=master
    :target: https://travis-ci.org/motom001/DoorPi

.. |pypi_License| image:: https://img.shields.io/pypi/l/DoorPi.svg
    :target: https://creativecommons.org/licenses/by-nc/4.0/
    :alt: CC BY-NC 4.0

.. |pypi_latest_version| image:: https://img.shields.io/pypi/v/DoorPi.svg?label=latest%20version
    :target: https://pypi.python.org/pypi/DoorPi
    :alt: Download


|pypi_License| |travis_status_master| |pypi_latest_version|


.. contents::
    :local:
    :depth: 2
    :backlinks: none


=============
Deutsch
=============
---------------
Einführung
---------------
Ziel des Projektes DoorPi ist die Steuerung einer Türsprechanlage mittels einem Einplatiniencomputer wie dem Raspberry Pi und dem Kommunikationsprotokoll `VoIP`_.

DoorPi ist ein Event-Action basierendes System. Es gibt Komponenten die Events auslösen und Komponenten, die aufgrund dieser Events reagieren. Dazu sollen Ereignisse (Events) wie "Drücken einer Türklingel" oder "RFID Chip xyz vorgehalten" die Auslöser von Aktionen (Actions) wie "Anruf bei Telefon xyz", "E-Mail an xxx" oder "Öffne Tür" sein.

---------------
Event-Quellen
---------------

Um diese Events zu registrieren, werden "DoorPi-Interfaces" genutzt, was z.B.:

* die GPIO-Pins
* ein PiFace 
* Dateien im Dateisystem des Pi (z.B. für Remote-Befehle über SSH)
* die serielle Schnittstelle (RDM6300 als NFC Reader)
* Webservice mit Authentifizierung
* VoIP-Telefon

sein können.

An jedes Event können beliebig viele Actions angefügt werden, die syncron oder asyncron ausgeführt werden. 

-----------------
Action-Empfänger
-----------------

Eine nicht vollständige Liste der Actions ist:

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

-----------------
Beispiele
-----------------

Ein mögliches Szenario ist:

#. Beim Druck eines Klingeltasters wird ein Anruf ausgelöst und gezielt eine Nummer angerufen (z.B. interne FritzBox Nummer \*\*613 aber auch Handynummern).
#. Der Bewohner kann mit der Außenstelle telefonieren und auf Wunsch die Tür remote öffnen, in dem eine definierte Taste (oder Tastenfolge) auf dem Telefon gedrückt wird (z.B. die Taste "#").
#. Der Bewohner vergisst das auflegen und DoorPi beendet selbst das Gespräch, sobald die Tür wieder geschlossen wurde.
#. DoorPi versendet eine E-Mail, dass es einen Anruf gab, jemand die Tür geöffnet hat und jemand ins Haus gegangen ist.

Mittlerweile gibt es auch Video-Support, so dass an der Haustür eine Kamera installiert werden kann und das Bild auf den Innenstationen angesehen werden kann, noch bevor das Gespräch angenommen wird.

-----------------
Installation
-----------------

Die Installationen werden `hier beschrieben <http://board.doorpi.org/Forum-4-Installation.html>`_

-----------------
Konfiguration
-----------------

Die Konfigurationen werden `hier beschrieben <http://board.doorpi.org/Forum-5-Konfiguration.html>`_

-----------------
DoorPi-Hilfe 
-----------------

Link zu Foren mit DoorPi Beiträgen:

`DoorPi Forum <http://board.doorpi.org/>`_

`[Haussteuerung] DoorPi (VoIP Wechselsprechanlage / Türsprechanlage mit Video-Support) <http://www.forum-raspberrypi.de/Thread-haussteuerung-doorpi-voip-wechselsprechanlage-tuersprechanlage-mit-video-support>`_

`DoorPI / VoIP Door-Intercomstation with Raspberry Pi <http://www.ip-symcon.de/forum/threads/26739-DoorPI-VoIP-Door-Intercomstation-with-Raspberry-Pi>`_


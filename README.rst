****************************************************
DoorPi: Open Source VoIP Türsprechanlage
****************************************************

|pypi_License| |pypi_latest_version| |travis_status_master| |code_climate_badge| |scrutinizer_status_master|

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
Ziel des Projektes DoorPi ist die Steuerung einer Türsprechanlage mittels einem Einplatiniencomputer wie dem Raspberry Pi und dem Kommunikationsprotokoll VoIP.

DoorPi ist ein Event-Action basierendes System. Es gibt Komponenten, die Events auslösen, und Komponenten, die aufgrund dieser Events reagieren. Dazu sollen Ereignisse (Events) wie "Drücken einer Türklingel" oder "RFID Chip xyz vorgehalten" die Auslöser von Aktionen (Actions) wie "Anruf bei Telefon xyz", "E-Mail an xxx" oder "Öffne Tür" sein.

---------------
Event-Quellen
---------------

Um diese Events zu registrieren, werden "DoorPi-Keyboards" genutzt, was z.B.:

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

Die Installationen werden `hier beschrieben <https://www.doorpi.org/forum/lexicon/lexicon/6-installation/>`_


-----------------
DoorPi-Hilfe 
-----------------

Link zu Foren mit DoorPi Beiträgen:

`DoorPi Forum <http://www.doorpi.org/forum/>`_

`DoorPi Lexikon / Wiki <http://www.doorpi.org/forum/>`_

`[Haussteuerung] DoorPi (VoIP Wechselsprechanlage / Türsprechanlage mit Video-Support) <http://www.forum-raspberrypi.de/Thread-haussteuerung-doorpi-voip-wechselsprechanlage-tuersprechanlage-mit-video-support>`_

`DoorPI / VoIP Door-Intercomstation with Raspberry Pi <http://www.ip-symcon.de/forum/threads/26739-DoorPI-VoIP-Door-Intercomstation-with-Raspberry-Pi>`_




=============
English
=============


---------------
Introduction
---------------

Aim of the DoorPi project is the realization of a door intercom station with a single board computer like the Raspberry Pi and the communication protocol VOIP.

DoorPi is an event-action based system. There are components which fire events, and components which react on these events. That means that events like "Doorbell pressed" or "RFID chip xyz detected" shall be the trigger for actions like "call telephne xyz", "send email to xyz" or "open door".


---------------
Event-Sources
---------------

For registering these events, so-called "DoorPi-Keyboards" are used, e.g

* GPIO pins
* a PiFace
* files in the filesystem of the PI (e.g. for remote commands via SSH)
* the serial port (e.g. with an RDM6300 as NFC reader)
* web service with authentification
* VOIP phone

To every event, any number of actions can be attached, which are executed synchronously or asynchronously.


-----------------
Action-Receivers
-----------------

A non-complete list of actions is:

* VOIP call to a predefined number
* VOIP call to a number which is read from a file
* end call
* send email
* execute program
* set an output pin
* write a status file
* read values from IP-Symcon or write them back

Via the combination of events and actions, almost all combinations are possible.


-----------------
Examples
-----------------

A thinkable scenario is:

#. when the doorbell button is pressed, a call is instantiated for calling a specific number (e.g. internal number of the FritzBox \*\*613, but also cell phone numbers)
#. the inhabitant can talk to the outside station and on demand open the door remotely, by pressing a defined key (or sequence of keys) on a telephone (e.g. the key "#")
#. the inhabitant forgets to end the call and DoorPi ends the call itself, as soon as the door was closed again
#. DoorPi sends an email that there was a call, somebody opened the door and somebody walked into the house

Meanwhile there is also video support, so that a camera can be installed at the door, and the image can be watched on the inside station even before the call is accepted


-----------------
Installation
-----------------
Installations are `described here <https://www.doorpi.org/forum/lexicon/lexicon/6-installation/>`_


=============
Changelog
=============

see `changelog.txt <https://github.com/motom001/DoorPi/blob/master/changelog.txt>`_


.. |travis_status_master| image:: https://travis-ci.org/motom001/DoorPi.svg?branch=master
    :target: https://travis-ci.org/motom001/DoorPi

.. |scrutinizer_status_master| image:: https://codeclimate.com/github/motom001/DoorPi/badges/gpa.svg
   :target: https://codeclimate.com/github/motom001/DoorPi
   :alt: Code Climate

.. |code_climate_badge| image:: https://scrutinizer-ci.com/g/motom001/DoorPi/badges/quality-score.png?b=master
   :target: https://scrutinizer-ci.com/g/motom001/DoorPi/
   
.. |pypi_License| image:: https://img.shields.io/pypi/l/DoorPi.svg
    :target: https://creativecommons.org/licenses/by-nc/4.0/
    :alt: CC BY-NC 4.0

.. |pypi_latest_version| image:: https://img.shields.io/pypi/v/DoorPi.svg?label=latest%20version
    :target: https://pypi.python.org/pypi/DoorPi
    :alt: Download

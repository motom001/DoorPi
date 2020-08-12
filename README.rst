DoorPi: Open Source VoIP Türsprechanlage
****************************************

|pypi_License|
|pypi_latest_version|
|travis_status_master|
|scrutinizer_status_master|
|code_climate_badge|

.. contents::
   :local:
   :depth: 2
   :backlinks: none

Deutsch
=======

Wichtiger Hinweis (Änderungen zum Ursprungsprojekt)
---------------------------------------------------

Durch die Vielzahl an Änderungen in den einzelnen Modulen ist dieser
Fork **nicht mehr kompatibel** mit `dem ursprünglichen Projekt`__.

Es wird empfohlen, die Konfigurationsdatei für diesen Fork von Grund auf
neu zu erstellen.  Ausführliche Informationen dazu sind im Webinterface
von DoorPi zu finden.

Falls bereits frühere Versionen dieses Projekts im Einsatz waren, wird
eine Lektüre des `Änderungsprotokolls`__ ausdrücklich empfohlen.

__ https://github.com/motom001/DoorPi
__ changelog.txt

Einführung
----------

Ziel des Projektes DoorPi ist die Steuerung einer Türsprechanlage
mithilfe eines Einplatiniencomputers wie dem Raspberry Pi und dem
Kommunikationsprotokoll VoIP.

DoorPi ist ein Event-Action-basierendes System.  Es gibt Komponenten,
die Events auslösen, und Komponenten, die aufgrund dieser Events
reagieren.  Dazu sollen Ereignisse (Events), wie z.B. das Drücken einer
Türklingel oder Vorhalten eines RFID-Chips, die Auslöser von Aktionen
(Actions) sein, wie etwa ein Anruf bei einer hinterlegten Telefonnummer,
das Versenden einer E-Mail oder das Auslösen des Türöffners.

Event-Quellen
-------------

Um diese Events zu registrieren, werden "DoorPi-Keyboards" genutzt.
Diese sind zum Beispiel:

* die GPIO-Pins
* ein PiFace
* Dateien im Dateisystem des Pi (z.B. für Remote-Befehle über SSH)
* die serielle Schnittstelle (RDM6300 als NFC Reader)
* Webservice mit Authentifizierung
* VoIP-Telefon

An jedes Event können beliebig viele Actions angefügt werden, die
synchron oder asynchron ausgeführt werden.

Action-Empfänger
----------------

Eine nicht vollständige Liste der Actions ist:

* VoIP-Anrufe starten oder auflegen
* E-Mail versenden
* Programm ausführen
* GPIO-Ausgänge ein- oder ausschalten
* Status-Datei schreiben
* Werte aus IP-Symcon lesen oder zurück schreiben
* ...

Durch die Kombination der Events und Actions ist eine Vielzahl an
Kombinationen möglich.

Beispiele
---------

Ein mögliches Szenario ist:

1. Beim Druck eines Klingeltasters wird ein Anruf ausgelöst und gezielt
   eine Nummer angerufen.
2. Der Bewohner kann mit der Außenstelle telefonieren und auf Wunsch den
   Türöffner auslösen, indem eine definierte Taste (oder Tastenfolge)
   auf dem Telefon gedrückt wird.
3. Der Bewohner vergisst das Auflegen und DoorPi beendet selbst das
   Gespräch, sobald die Tür wieder geschlossen wurde.
4. DoorPi versendet eine E-Mail, dass es einen Anruf gab,
   jemand die Tür geöffnet hat und jemand ins Haus gegangen ist.

Installation
------------

*   ArchLinuxARM: Ein PKGBUILD ist `im AUR verfügbar`__.
    Gestartet wird mit ``systemctl start doorpi.service``
    Für automatischen Start beim Hochfahren:
    ``systemctl enable doorpi.service``
*   Raspbian und andere: Die Installation dieses Forks geschieht
    mithilfe der Python setuptools.  Abhängigkeiten müssen
    gegebenenfalls vorher manuell installiert werden. ::

        git clone https://github.com/Wuestengecko/DoorPi.git
        cd DoorPi
        python setup.py build
        sudo python setup.py install --prefix=/usr/local

    Für weitere Informationen siehe `die Installationsanweisungen im
    offiziellen Forum`__.

__ https://aur.archlinux.org/packages/doorpi
__ http://www.doorpi.org/forum/board/21-installation/

DoorPi-Hilfe
------------

Link zu Foren mit DoorPi Beiträgen:

* `DoorPi Forum`__
* `[Haussteuerung] DoorPi
  (VoIP Wechselsprechanlage / Türsprechanlage mit Video-Support)`__
* `DoorPI / VoIP Door-Intercomstation with Raspberry Pi`__

__ http://www.doorpi.org/forum/
__ http://www.forum-raspberrypi.de/Thread-haussteuerung-doorpi-voip-wechselsprechanlage-tuersprechanlage-mit-video-support
__ http://www.ip-symcon.de/forum/threads/26739-DoorPI-VoIP-Door-Intercomstation-with-Raspberry-Pi

English
=======

Important Notes (Differences to the original project)
-----------------------------------------------------

Due to a variety of changes in all modules, this fork **is no longer
compatible** with `the original project`__.

It is recommended to rewrite the configuration from scratch.  For
extensive information on the supported configuration, please refer to
the built-in web interface.

If you used a previous version of this project, it is recommended to
also review the `changelog`__.

__ https://github.com/motom001/DoorPi
__ changelog.txt

Introduction
------------

Goal of the DoorPi project is the realization of a door intercom station
with a single board computer like the Raspberry Pi and the communication
protocol VOIP.

DoorPi is an event-action based system.  There are components which fire
events, and components which react on these events.  That means that
events like "Doorbell pressed" or "RFID chip xyz detected" can trigger
actions like "call telephone xyz", "send email to xyz" or "open door".

Event-Sources
-------------

For registering these events, so-called "DoorPi-Keyboards" are used.
Examples include:

* GPIO pins
* A PiFace
* Files in the filesystem of the PI (e.g. for remote commands via SSH)
* The serial port (e.g. with an RDM6300 as NFC reader)
* Web service with authentification
* VOIP phone

Each event can trigger the execution of any number of actions, which are
executed synchronously or asynchronously.

Action-Receivers
----------------

A non-complete list of actions is:

* Start or end a VoIP call
* Send an e-mail
* Execute a program
* Set a GPIO output pin
* Write a status file
* Read values from IP-Symcon or write them back
* ...

By combining different events and actions, a great number of
combinations is possible.

Examples
--------

A possible scenario is:

1. When the doorbell is pressed, a call to a specific number is started.
2. The inhabitant can talk to the outside station and on demand open the
   door remotely by pressing a key (or key sequence) on the telephone.
3. The inhabitant forgets to end the call and DoorPi ends the call
   itself, as soon as the door is closed again.
4. DoorPi sends an email that there was a call, somebody opened the door
   and somebody walked into the house

Installation
------------

* ArchLinuxARM: A PKGBUILD is `available in the AUR`__.
  Start DoorPi with ``systemctl start doorpi.service``
  To automatically start it after booting, use
  ``systemctl enable doorpi.service``
*   Others (including Raspbian):
    Download and install this fork with python setuptools.
    You need to take care of dependencies yourself::

        git clone https://github.com/Wuestengecko/DoorPi.git
        cd DoorPi
        python setup.py build
        sudo python setup.py install --prefix=/usr/local

    For more information see `the official forum`__.

__ https://aur.archlinux.org/packages/doorpi
__ http://www.doorpi.org/forum/board/21-installation/

Changelog
=========

See the `changelog for published versions`__.
For developmental versions, also see `the commit history`__.

__ https://github.com/Wuestengecko/DoorPi/blob/master/changelog.txt
__ https://github.com/Wuestengecko/DoorPi/commits/master


.. |pypi_License| image::
   https://img.shields.io/pypi/l/DoorPi.svg
   :target: https://creativecommons.org/licenses/by-nc/4.0/
   :alt: CC BY-NC 4.0

.. |pypi_latest_version| image::
   https://img.shields.io/pypi/v/DoorPi.svg?label=latest%20version
   :target: https://pypi.python.org/pypi/DoorPi
   :alt: Download

.. |travis_status_master| image::
   https://travis-ci.org/motom001/DoorPi.svg?branch=master
   :target: https://travis-ci.org/motom001/DoorPi

.. |scrutinizer_status_master| image::
   https://scrutinizer-ci.com/g/motom001/DoorPi/badges/quality-score.png?b=master
   :target: https://scrutinizer-ci.com/g/motom001/DoorPi/

.. |code_climate_badge| image::
   https://api.codeclimate.com/v1/badges/a0ea0a3f3f1467bce688/maintainability
   :target: https://codeclimate.com/github/Wuestengecko/DoorPi/maintainability
   :alt: Maintainability

.. vim:set tw=72:

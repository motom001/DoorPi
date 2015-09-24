****************************************************
DoorPi: VoIP Door-Intercomstation with Raspberry Pi
****************************************************

|travis_status_master| |code_climate_badge| |scrutinizer_status_master| 

:DoorPi @ `PyPi`_: 
    |pypi_latest_version| |pypi_License|
    
    |pypi_downloads_day| |pypi_downloads_week| |pypi_downloads_month|

:DoorPi @ `GitHub`_: 

    |github_issues_open| |github_issues_all|
    
    |github_watchs| |github_stars| |github_forks|


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

DoorPi ist ein Event-Action basierendes System. Es gibt Komponenten die Events auslösen und Komponenten die aufgrund dieser Events reagieren. Dazu sollen Ereignisse (Events) wie "Drücken einer Türklingel" oder "RFID Chip xyz vorgehalten" die Auslöser von Aktionen (Actions) wie "Anruf bei Telefon xyz", "E-Mail an xxx" oder "Öffne Tür" sein.

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

via `PyPi`_:

.. code-block:: bash

   sudo pip install doorpi &&
   doorpi_cli --trace

via `GitHub`_:

.. code-block:: bash

   sudo rm -r -f /tmp/DoorPi
   git clone https://github.com/motom001/DoorPi.git /tmp/DoorPi
   cd /tmp/DoorPi
   sudo python setup.py install
   doorpi_cli --trace

   
-----------------
Konfiguration
-----------------

Der Start von DoorPi endet mit der Ausgabe der Weboberfläche-URL wie hier:

   2015-09-10 17:52:28,085 [INFO]   [doorpi.status.webserver] DoorPiWeb URL is http://raspberrypi:53540/
   
Aktuell bin ich noch nicht dazu gekommen, die Config pro Gerät (GPIO, PiFace, ...) zu individualisieren.
In der Weboberfläche ist auf dem Startbildschirm die Übersicht der Module (z.B. GPIO). Rechts von dem Modul gibt es den Button Info. 
In der Info-Seite findest Du neben der Beschreibung auch die möglichen Parameter mit default-Werten.
Parallel dazu gibt es in der Navigation den Konfig-Editor. Dort kannst Du die Config bearbeiten, wenn Du weißt, welche Parameter wo hin gehören.
Auch die Config abspeichern kannst Du in der Übersicht.

-----------------
Daemon
-----------------

Anleitung um DoorPi als Daemon einzurichten ist hier zu finden:
https://github.com/motom001/DoorPi/tree/master/doorpi/docs/service

Es sollte aber auf jeden Fall der `BASE_PATH <https://github.com/motom001/DoorPi/blob/master/doorpi/docs/service/doorpi#L17>`_ auf den Ablageort der Config-Datei angepasst werden.

-----------------
DoorPi Threads
-----------------

Link zu Foren mit DoorPi Threads:

:forum-raspberrypi.de: `[Haussteuerung] DoorPi (VoIP Wechselsprechanlage / Türsprechanlage mit Video-Support) <http://www.forum-raspberrypi.de/Thread-haussteuerung-doorpi-voip-wechselsprechanlage-tuersprechanlage-mit-video-support>`_

:ip-symcon.de: `DoorPI / VoIP Door-Intercomstation with Raspberry Pi <http://www.ip-symcon.de/forum/threads/26739-DoorPI-VoIP-Door-Intercomstation-with-Raspberry-Pi>`_

=============
English
=============
---------------
Introduction
---------------

coming soon

---------------
Event-Sorces
---------------

coming soon

-----------------
Action-Receiver
-----------------

coming soon

-----------------
Examples
-----------------

coming soon

-----------------
Installation
-----------------

via `PyPi`_:

.. code-block:: bash

   sudo pip install doorpi &&
   sudo doorpi_cli --trace

via `GitHub`_:

.. code-block:: bash

   sudo rm -r -f /tmp/DoorPi
   git clone https://github.com/motom001/DoorPi.git /tmp/DoorPi
   cd /tmp/DoorPi
   sudo python setup.py install
   doorpi_cli --trace

-----------------
Configuration
-----------------

coming soon

-----------------
Daemon
-----------------

The readme to install doorpi as daemon is here:
https://github.com/motom001/DoorPi/tree/master/doorpi/docs/service

But you should change the `BASE_PATH <https://github.com/motom001/DoorPi/blob/master/doorpi/docs/service/doorpi#L17>`_ to the path of the config file.

.. _VoIP: https://de.wikipedia.org/wiki/IP-Telefonie
.. _PyPi: https://pypi.python.org/pypi/DoorPi
.. _GitHub: https://github.com/motom001/DoorPi
.. _GitHubDaemonReadme: https://github.com/motom001/DoorPi/tree/master/doorpi/docs/service
.. _GitHubDaemonFileLine17: https://github.com/motom001/DoorPi/blob/master/doorpi/docs/service/doorpi#L17

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

.. |pypi_downloads_day| image:: https://img.shields.io/pypi/dd/DoorPi.svg
    :target: https://pypi.python.org/pypi/DoorPi#downloads
    :alt: Downloads last day

.. |pypi_downloads_week| image:: https://img.shields.io/pypi/dw/DoorPi.svg
    :target: https://pypi.python.org/pypi/DoorPi#downloads
    :alt: Downloads last week

.. |pypi_downloads_month| image:: https://img.shields.io/pypi/dm/DoorPi.svg
    :target: https://pypi.python.org/pypi/DoorPi#downloads
    :alt: Downloads last month


.. |github_issues_open| image:: https://img.shields.io/github/issues/motom001/DoorPi.svg
    :target: https://github.com/motom001/DoorPi/issues
    :alt: open issues on github

.. |github_issues_all| image:: https://img.shields.io/github/issues-raw/badges/shields.svg
    :target: https://github.com/motom001/DoorPi/issues?utf8=%E2%9C%93&q=is%3Aissue
    :alt: all issues on github

.. |github_watchs| image:: https://img.shields.io/github/watchers/motom001/DoorPi.svg?style=social&label=watchers
    :target: https://github.com/motom001/DoorPi/watchers

.. |github_stars| image:: https://img.shields.io/github/stars/motom001/DoorPi.svg?style=social&label=stars
    :target: https://github.com/motom001/DoorPi/stargazers

.. |github_forks| image:: https://img.shields.io/github/forks/motom001/DoorPi.svg?style=social&label=forks
    :target: https://github.com/motom001/DoorPi/network

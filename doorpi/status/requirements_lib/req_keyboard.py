#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

REQUIREMENT = dict(
    fulfilled_with_one = True,
    text_description = '''Die Aufgabe von einem Keyboard innerhalb von DoorPi ist es, Eingaben und Ausgaben zu steuern. Keyboard bezieht sich dabei nicht auf die Tastertur, sondern auf ein Brett mit Knöpfen und LEDs.
DoorPi ist in der Lage mehrere Keyboards gleichzeitig zu verwalten. Dazu muss in der Konfiguration zuerst eine Zuordnung getroffen werden, welchen frei ausgedachten aber eindeutigen Namen das Keyboard bekommmt (KeyboardName) und von welchem Typ das Keyboard ist.
Diese Zuordnung findet in einer Konfigurations-Sektion "keyboards" statt. Danach kann jedes Keyboard drei weitere Sektionen besitzen:
<ol>
<li>allgemeine und Keyboard-spezifische Konfigurationsparameter (Sektionsname "[KeyboardName]")</li>
<li>Auflistung der InputPins (Sektionsname "[KeyboardName]_InputPins") - wobei Pin auch eine Zeichenkette sein kann wie im Beispiel vom RFID-Reader</li>
<li>Auflistung der OutputPins (Sektionsname "[KeyboardName]_OutputPins") mit Pinnummer und sprechendem Namen</li>
</ol>

Die OutputPins können später entweder mit der Pinnummer oder dem sprechenden Namen angesprochen werden. Deshalb sollte der sprechende Name eindeutig sein.

Beispiel (alles nach einem # sind Kommentare):
<code>
[keyboards]
virtuelles = filesystem
rfid = rdm6300

[virtuelles]
base_path_input = !BASEPATH!/keyboards/virtuelles/inputpins # Pfad in dem dann die Input-Dateien zu finden sind
base_path_output = !BASEPATH!/keyboards/virtuelles/outputpins # Pfad in dem dann die Output-Dateien zu finden sind
reset_input = true # Ausgangszustand der Eingabe-Datei soll wiederhergestellt werden, wenn Signal erkannt wurde

[virtuelles_InputPins]
klingel = out:tueroeffner:0,1,3 # Wenn diese Datei eine '1' beinhaltet, dann soll ein Ausgane mit dem Namen tueroeffner gesteuert werden

[virtuelles_OutputPins]
ausgang = tueroeffner # die Datei "ausgang" wird Dateisystem angelegt, aber innerhalb von DoorPi mit "tueroeffner" angesprochen
ausgang2 = fensteroeffner # die Datei "ausgang2" wird Dateisystem angelegt, aber innerhalb von DoorPi mit "fensteroeffner" angesprochen

[rfid]
# keine weitere spezielle Konfiguration, da uns die Default-Werte vollkommen ausreichen
# theoretisch könnte die ganze Sektion weggelassen werden, da sie leer ist

[rfid_InputPins]
1234567 = out:tueroeffner,1,0,3
2345678 = out:fensteroeffner,1,0,3

# eine Sektion [rfid_OutputPins] macht keinen Sinn, da ein RFID-Reader nichts ausgeben kann :)
</code>

Ergebnis des Beispiels ist, dass:
<ol>
    <li>zwei Keyboards innerhalb von DoorPi registiert werden - das eine dateibasierend mit dem Namen "virtuell", das andere ein RFID-Reader mit dem Namen "rfid"</li>
    <li>dem virtuellen Keyboard alle nötigen Parameter mitgegeben werden, beim rfid Keyboard nur die Default-Parameter genutzt werden.</li>
    <li>ein InputPin für das virtuelle Keyboard angelegt wird</li>
    <li>wenn die Datei <code>!BASEPATH!/keyboards/virtuelles/inputpins/klingel</code> eine 1 als Inhalt bekommt, wird
        <ul>
            <li>Ausgang tueroeffner (in dem Fall die Datei !BASEPATH!/keyboards/virtuelles/outputpins/ausgang)</li>
            <li>neu geschrieben und bekommt am Anfang den Inhalt 1</li>
            <li>es wird drei Sekunden gewartet</li>
            <li>und die Datei wird neu geschrieben, diesmal mit dem Inhalt 0</li>
        </ul>
    </li>
    <li>ähnliches für das rfid Keyboard definiert wurde:
        <ul>
            <li>der RFID-Chip mit dem Code "1234567" öffnet den tueroeffner</li>
            <li>der RFID-Chip mit dem Code "2345678" öffnet den fensteroeffner</li>
        </ul>
    </li>
</ol>

Wobei !BASEPATH! für das Home-Verzeichnis von DoorPi steht (meistens "/home/DoorPi").
''',
    events = [
        dict( name = 'OnKeyPressed', description = 'Es wurde eine Taste als betätigt gemeldet. Das kann je nach Keyboard OnKeyUp oder OnKeyDown sein.'),
        dict( name = 'OnKeyUp', description = 'Eine Taste wurde wieder losgelassen.'),
        dict( name = 'OnKeyDown', description = 'Eine Taste wurde gedrückt, aber noch nicht wieder los gelassen.'),
        dict( name = 'OnKeyPressed_[PinName]', description = 'Gleich wie OnKeyPressed aber beinhaltet außerdem den Pin-Namen um gezielter mit Actions reagieren zu können.'),
        dict( name = 'OnKeyUp_[PinName]', description = 'Gleich wie OnKeyUp aber beinhaltet außerdem den Pin-Namen um gezielter mit Actions reagieren zu können.'),
        dict( name = 'OnKeyDown_[PinName]', description = 'Gleich wie OnKeyDown aber beinhaltet außerdem den Pin-Namen um gezielter mit Actions reagieren zu können.'),
        dict( name = 'OnKeyPressed_[KeyboardName]_[PinName]', description = 'Gleich wie OnKeyPressed aber beinhaltet außerdem den Keyboard-Namen und den Pin-Namen um ganz exakt mit Actions reagieren zu können.'),
        dict( name = 'OnKeyUp_[KeyboardName]_[PinName]', description = 'Gleich wie OnKeyUp aber beinhaltet außerdem den Keyboard-Namen und den Pin-Namen um ganz exakt mit Actions reagieren zu können.'),
        dict( name = 'OnKeyDown_[KeyboardName]_[PinName]', description = 'Gleich wie OnKeyDown aber beinhaltet außerdem den Keyboard-Namen und den Pin-Namen um ganz exakt mit Actions reagieren zu können.')
    ],
    configuration = [
        dict( section = 'keyboards', key = '*', type = 'string', default = 'dummy', mandatory = False, description = 'In der Sektion werden die genutzten Keyboards mit Namen und Typ im Stil <code>[KeyboardName] = [KeyboardTyp]</code> aufgelistet. Die komplette Sektion wird ausgelesen.'),
        dict( section = '[KeyboardName]', key = 'bouncetime', type = 'float', default = '2000', mandatory = False, description = 'bouncetime ist ein softwareseitiger Prellschutz innerhalb dessen Zeit in ms alle weiteren Ereignisse ignoriert werden.'),
        dict( section = '[KeyboardName]', key = 'polarity', type = 'integer', default = '0', mandatory = False, description = 'polarity verdreht die Logik der Eingänge, so dass HIGH-Pegel = LOW-Pegel und umgedreht. Hat aber nur auf die Eingänge Auswirkung!'),
        dict( section = '[KeyboardName]_InputPins', key = '*', type = 'string', default = '', mandatory = False, description = 'Auflistung der Eingabeschnittstellen im Format <code>[PinName] = [Action]</code>. Bitte dazu die möglichen Actions und deren Syntax beachten!'),
        dict( section = '[KeyboardName]_OutputPins', key = '*', type = 'string', default = '', mandatory = False, description = 'Auflistung der Eingabeschnittstellen im Format <code>[PinName] = [SprechenderPinName]</code> - z.B. gibt es den GPIO Ausgang 27 für den Türöffner, so wäre die Syntax <code>27 = Tueroeffner</code>. Umlaute und Sonderzeichen sollten vermieden werden!')
    ],
    libraries = { # nicht als dict(), da es sonst Probleme mit dem Punkt in RPi.GPIO als Key gibt
        'pifacedigitalio': dict(
            text_warning =          '''Neben der reinen Installation vom Python-Modul pifacedigitalio ist es auch wichtig SPI am System zu aktivieren (siehe Links).
Außerdem muss bei Bestellungen darauf geachtet werden, dass es zwei Versionen gibt (<a href="https://www.rasppishop.de/Piface-Digital-Erweiterung-fuer-Raspberry-Pi">PiFace digital 1</a> und <a href="https://www.rasppishop.de/PiFace-Digital-2-Erweiterungsplatine-/-Modul-fuer-den-Raspberry-Pi-Modell-B-">PiFace digital 2</a>)''',
            text_description =      'Das Python-Modul pifacedigitalio ist der "Treiber" für die PiFace Hardware.',
            text_installation =     '',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import pifacedigitalio</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/configparser.html',
                'PiFace Beschreibung auf piface.org.uk': 'http://www.piface.org.uk/products/piface_digital/',
                'Installationsanleitung auf github': 'http://piface.github.io/pifacedigitalio/installation.html',
                'SPI und I2C aktivieren': 'http://raspberry.tips/faq/raspberry-pi-spi-und-i2c-aktivieren/'
            }
        ),
        'RPi.GPIO': dict(
            text_warning =          '',
            text_description =      'RPi.GPIO kümmert sich um die Ein- und Ausgaben der GPIO Schnittstelle eines Raspberry Pi.',
            text_installation =     'Die Installation ist sehr gut <a href="http://sourceforge.net/p/raspberry-gpio-python/wiki/install/">auf Sourceforge</a> beschrieben.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import RPi.GPIO</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'www.raspberrypi.org': {
                    'GPIO Overview': 'https://www.raspberrypi.org/documentation/hardware/raspberrypi/gpio/README.md',
                    'GPIO Usage': 'https://www.raspberrypi.org/documentation/usage/gpio/README.md'
                },
                'RPi.GPIO on pypi': 'https://pypi.python.org/pypi/RPi.GPIO',
                'Installationsanleitung auf Sourceforge': 'http://sourceforge.net/p/raspberry-gpio-python/wiki/install/'
            }
        ),
        'serial': dict(
            text_warning =          '',
            text_description =      '''
Hier die Beschreibung aus der <a href="https://github.com/motom001/DoorPi/blob/master/doorpi/keyboard/from_rdm6300.py">from_rdm6300.py</a>, die <a href="https://github.com/msmolny">msmolny</a> netterweise erstellt hat.

<pre>
  Configuration
  -------------

  1. Define a new keyboard of type 'rdm6300'
  2. Define inputPins section for that keyboard
  3. Each RFID tag has a decimal number printed 
     on the surface. This is the Input PIN number. 
     Define this number and an appropriate action.

  Sample:

  [keyboards]
  rfidreader = rdm6300
  ...
  [rfidreader_InputPins]
  1234567 = out:Tueroeffner,1,0,3
  2345678 = out:Tueroeffner,1,0,3

  That's all...


  Hardware Connections
  --------------------

  RDM6300 Pin Layout
  +-------------------------+
  |                         |
  | (1) ANT1                |
  | (2) ANT2                |
  | P2                      |
  |                         |
  |                         |
  |                         |
  |                     P1  |
  |             +5V(DC) (5) |
  | P3              GND (4) |
  | (3) GND             (3) |
  | (2) +5V(DC)      RX (2) |
  | (1) LED          TX (1) |
  |                         |
  +-------------------------+

  Connect one of the two +5V(DC) and one of the two GND to 
  5V (Pin 2 on the RaspberryPi Board) and to GND (Pin 6 on 
  the RaspberryPi Board). As I used a ribbon cable, the 
  simplest way was to connect to (4) and (5) of P1 from the RDM6300. 
 
  Then, connect TX (pin (1) of P1) to RXD from the UART (Pin 10 
  on the RaspberryPi Board) - BUT NOT DIRECTLY, OTHERWISE YOU 
  MIGHT DAMAGE YOUR RASPBERRY PI!!!
  The RaspberryPi expects 3,3V level on the UART Pins, but the 
  RDM6300 delivers 5V. 

  Simplest solution for this is a voltage divider via resistors:
     RDM6300 P1(1) <--- Resistor R1 ---> RasPi Board(Pin 10)
     GND           <--- Resistor R2 ---> RasPi Board(Pin 10) 
  Ideal solution: R1=5k, R2=10k, this will deliver exactly 3,3V 
                  to RasPi Board(Pin 10)
  Alternative solution: As most RaspberryPi bundles only contain 
                        10k resistors, you might either use 2 
                        10k resistors in parallel to get a 5k 
                        resistor, or simply use 10k for R1 instead.
                        R1=R2=10k will deliver 2,5V to RasPi 
                        Board(Pin 10), but that works also.

  Reference: I used this resource to learn how to work with RDM6300, 
             how to connect it to the RaspberryPi and how to handle
             RFID data: http://kampis-elektroecke.de/?page_id=3248
</pre>
''',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import serial</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                dict( section = '[KeyboardName]', key = 'port', type = 'string', default = '/dev/ttyAMA0', mandatory = False, description = ''),
                dict( section = '[KeyboardName]', key = 'baudrate', type = 'integer', default = '9600', mandatory = False, description = ''),
                dict( section = '[KeyboardName]', key = 'dismisstime', type = 'integer', default = '5', mandatory = False, description = ''),
            ],
            text_links = {
                'serial @ pypi': 'https://pypi.python.org/pypi/serial'
            }
        ),
        'watchdog': dict(
            text_warning =          'Häufiges Lesen und Schreiben von SD-Karten wie im RPi können deren Verschleiß fördern. Eventuell sollte auf tmpfs Verzeichnisse ausgewichen werden.',
            text_description =      '''Das Python-Modul watchdog wird genutzt um ein dateibasierendes Keyboard zu erstellen.
So können entweder zu Testzwecken ohne Hardware-Aufbau Events und Actions getestet werden oder es kann als Schnittstelle zu anderen Systemen dienen,
die per SSH-Befehle die Dateien schreiben und lesen, die auch vom virtuellen keyboard verarbeitet werden.
Dabei kann eingestellt werden, in welchem Ordner die Dateien liegen, die jeweils als Ein- und Ausgabe fungieren und ob die Eingabe Dateien nach Erkennung eines Events durch das Filesystem-Keyboard wieder zurück in den Ausgangszustand versetzt werden.
''',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import ConfigParser</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                dict( section = '[KeyboardName]', key = 'base_path_input', type = 'string', default = '', mandatory = False, description = 'Der Pfad in dem die Eingangspins angelegt werden'),
                dict( section = '[KeyboardName]', key = 'base_path_output', type = 'string', default = '', mandatory = False, description = 'Der Pfad in dem die Eingangspins angelegt werden'),
                dict( section = '[KeyboardName]', key = 'reset_input', type = 'boolean', default = 'True', mandatory = False, description = 'Gibt an ob die Dateien nach Erkennung eines Events durch das Filesystem-Keyboard wieder zurück in den Ausgangszustand versetzt werden')
            ],
            text_links = {
                'watchdog @ pypi': 'https://pypi.python.org/pypi/watchdog'
            }
        )
    }
)

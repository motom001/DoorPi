#!/usr/bin/env python
# -*- coding: utf-8 -*-
from doorpi.keyboard.AbstractBaseClass import KeyboardAbstractBaseClass, HIGH_LEVEL
import doorpi

import threading
import time
from pyfingerprint.pyfingerprint import PyFingerprint

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)


def get(**kwargs): return Fingerprint(**kwargs)


class Fingerprint(KeyboardAbstractBaseClass):
    name = 'Fingerprint Reader'

    def readFingerprint(self):
        try:
            # Sensor initialisieren
            sensor = PyFingerprint(
                self.__port, self.__baudrate, self.__sensoraddr, self.__password)
            if not sensor.verifyPassword():
                logger.warning(
                    'The given fingerprint sensor password is wrong!')
                return None

            logger.debug('Currently used templates: ' +
                         str(sensor.getTemplateCount()) + '/' + str(sensor.getStorageCapacity()))
            # Sensor-Lesen & Event-Handling
            logger.debug('readFingerprint() started for %s', self.__timeout)
            while (not self._shutdown and self.__active):
                # Falls der Sensor nicht permanent aktiv ist und das Aktivitätsintervall überschritten ist - Abbruch
                if (self.__timeout > 0 and (time.time() > self.__timeout)):
                    self.__active = False
                    return None

                if (sensor.readImage()):
                    # Characteristics aus dem gelesenen Fingerabdruck auslesen und hinterlegen
                    sensor.convertImage(0x01)

                    # Datenbank nach diesen Characteristics durchsuchen
                    result = sensor.searchTemplate()
                    positionNumber = result[0]
                    accuracyScore = result[1]

                    # Input-Pin entsprechend der gefundenen Position aktivieren
                    self.last_key = positionNumber
                    self.last_key_time = time.time()
                    logger.debug('Found template at position #' +
                                 str(positionNumber))
                    logger.debug('The accuracy score is: ' +
                                 str(accuracyScore))

                    # Finger entweder gar nicht oder nicht exakt genug erkannt.
                    if (positionNumber == -1) or (accuracyScore < self.__security):
                        # Finger unbekannt - Event ausloesen
                        doorpi.DoorPi().event_handler('OnFingerprintFoundUnknown', __name__)
                    else:
                        # Finger bekannt - Event ausloesen
                        doorpi.DoorPi().event_handler('OnFingerprintFoundKnown', __name__)
                        # Dem Finger zugeordnete Events auslösen
                        if (self.last_key in self._InputPins):
                            self._fire_OnKeyDown(self.last_key, __name__)
                            self._fire_OnKeyPressed(self.last_key, __name__)
                            self._fire_OnKeyUp(self.last_key, __name__)

        except Exception as ex:
            logger.exception(ex)

    def __init__(self, input_pins, output_pins, keyboard_name, conf_pre, conf_post, *args, **kwargs):
        self.keyboard_name = keyboard_name
        self._InputPins = map(int, input_pins)
        self._OutputPins = map(int, output_pins)
        self.last_key = ""
        self.last_key_time = 0
        self.__timeout = 0

        # Spezielle Handler fuer (Un-)bekannte Finger registrieren
        doorpi.DoorPi().event_handler.register_event(
            'OnFingerprintFoundUnknown', __name__)
        doorpi.DoorPi().event_handler.register_event(
            'OnFingerprintFoundKnown', __name__)
        # Config-Eintraege lesen, falls dort vorhanden.
        section_name = conf_pre + 'keyboard' + conf_post
        self.__port = doorpi.DoorPi().config.get(section_name, 'port', '/dev/ttyAMA0')
        self.__baudrate = doorpi.DoorPi().config.get_int(section_name, 'baudrate', 57600)
        self.__sensoraddr = doorpi.DoorPi().config.get(
            section_name, 'address', 0xFFFFFFFF)
        self.__password = doorpi.DoorPi().config.get(
            section_name, 'password', 0x00000000)
        self.__security = doorpi.DoorPi().config.get_int(section_name, 'security', 70)

        # Events für hinterlegte InputPins registrieren (damit diese auch ausgeloest werden)
        for input_pin in self._InputPins:
            self._register_EVENTS_for_pin(input_pin, __name__)

        # Dauerbetrieb oder nur auf Kommando? (Trigger-Pin definiert?)
        self.__active = (len(self._OutputPins) == 0)
        self._shutdown = False

        if self.__active:
            logger.debug('No trigger pin defined! Running permanently')
            # Thread für den eigtl Lesevorgang starten
            self._thread = threading.Thread(target=self.readFingerprint)
            self._thread.daemon = True
            self._thread.start()
            self.register_destroy_action()

    def destroy(self):
        if self.is_destroyed:
            return

        self._shutdown = True
        doorpi.DoorPi().event_handler.unregister_source(__name__, True)
        self.__destroyed = True

    def status_input(self, tag):
        return (tag == self.last_key)

    def set_output(self, pin, value, log_output=True):
        parsed_pin = doorpi.DoorPi().parse_string('!' + str(pin) + '!')
        if parsed_pin != '!' + str(pin) + '!':
            pin = parsed_pin
            logger.debug('out(parsed pin = %s)', parsed_pin)

        pin = int(pin)
        value = int(value)
        log_output = str(log_output).lower() in HIGH_LEVEL

        if pin not in self._OutputPins:
            return False

        if log_output:
            logger.debug('out(pin = %s, value = %s, log_output = %s)',
                         pin, value, log_output)

        # Aktivieren oder deaktivieren?
        old_state = self.__active
        self.__active = (value > 0)
        # Timeout-Intervall anpassen (bei 0 stoppt der Vorgang sowohl dadurch als auch da active false wird)
        self.__timeout = time.time() + value

        # Falls noch kein Lesevorgang laeuft, diesen ggf. starten
        if self.__active and self.__active != old_state:
            # Thread fuer den eigtl Lesevorgang starten
            self._shutdown = False
            self._thread = threading.Thread(target=self.readFingerprint)
            self._thread.daemon = True
            self._thread.start()
            self.register_destroy_action()

        return True

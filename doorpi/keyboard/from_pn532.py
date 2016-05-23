# -*- coding: utf-8 -*-
#
#  Configuration
#  -------------
#
#  1. Define a new keyboard of type 'pn532'
#  2. Define inputPins section for that keyboard
#
#  Sample:
#
#  [keyboards]
#  nfcreader = pn532
#
#  [nfcreader_keyboard]
#  TODO
#  device = tty:AMA0:pn532  
#
#  [nfcreader_InputPins]
#  1234 = **623
#  #calls **623 when tag-ID 1234 is scanned, logs user1 for this action (NOT the ID itself unless you are using debug mode)
#
#  [EVENT_OnKeyPressed_nfcreader.1234]
#  00 = call:**622
#
#  /TODO
#  That's all...
#
#  Hardware Connections
#  --------------------
#
#  For this keyboard we are using UART connection
#  Connect pn532 and Raspberry Pi as follows:
#  PN532   --   Raspberry Pi
#  VCC -- 5V
#  GND -- GND
#  RX -- GPIO 14 (TX)
#  TX -- GPIO 15 (RX)
#
#  IMPORTANT  --- IMPORTANT  ---- IMPORTANT  --- IMPORTANT  ---- IMPORTANT  --- IMPORTANT
#  TODO
#  you will also need the libnfc and nfcpy for this to work
#  
#  1) libnfc:  
#     sudo apt-get install autoconf libtool libpcsclite-dev libusb-dev
#     cd /home/pi
#     mkdir src
#     cd src
#     wget https://github.com/nfc-tools/libnfc/archive/master.zip
#     rename master.zip libnfc.zip
#     unzip libnfc.zip
#     cd libnfc --> ANPASSEN!!!!
#     sudo mkdir /etc/nfc
#     sudo mkdir /etc/nfc/devices.d
#     sudo cp contrib/libnfc/pn532_uart_on_rpi.conf.sample /etc/nfc/devices.d/pn532_uart_on_rpi.conf
#     add the line 
#            allow_intrusive_scan = true  <-- checken, ob das wirklich gebraucht wird und was das macht
#     to file /etc/nfc/devices.d/pn532_uart_on_rpi.conf
#     cd /home/pi/src/libnfc <-- anpassen
#     touch NEWS
#     touch README
#     autoreconf -vis
#     ./configure --with-drivers=pn532_uart --sysconfdir=/etc --prefix=/usr
#     sudo make clean
#     sudo make install all
#     cd examples
#     sudo ./nfc-poll
#     hold a tag near the reader and you should get an output similar to this:
#                 SAMPLE-OUTPUT einfügen
#  2) nfcpy
#     install following this: http://nfcpy.org/latest/topics/get-started.html#installation
#     be sure that serial console is deactivated in kernel (cmdline.txt or raspi-config)
#     test nfcpy using
#         python tagtool.py --device tty:AMA0:pn532
#     you should see output similar to
#                 SAMPLE-OUTPUT einfügen
#     copy source-dir to pythons libdir:
#     sudo cp -r nfc /usr/local/lib/python2.7/dist-packages/nfc   <--- CHECKEN!
#  /TODO

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import threading
from doorpi.keyboard.AbstractBaseClass import KeyboardAbstractBaseClass, HIGH_LEVEL, LOW_LEVEL
import doorpi
import nfc


def get(**kwargs): return pn532(**kwargs)


class pn532(KeyboardAbstractBaseClass):
    name = 'pn532 nfc keyboard'

    def pn532_recognized(self, tag):
        try:
            logger.debug("tag: %s", tag)
            hmm = str(tag)
            ID = str(hmm.split('ID=')[-1:])[2:-2]
            logger.debug("ID: %s", ID)
            if ID in self._InputPins:
                logger.debug("ID gefunden: %s", ID)
                self.last_key = ID
                self._fire_OnKeyDown(self.last_key, __name__)
                self._fire_OnKeyPressed(self.last_key, __name__)
                self._fire_OnKeyUp(self.last_key, __name__)
                doorpi.DoorPi().event_handler('OnFoundKnownTag', __name__)
                logger.debug("last_key is %s", self.last_key)
        except Exception as ex:
            logger.exception(ex)
        finally:
            logger.debug("pn532_recognized thread ended")

    def pn532_read(self):
        try:
            while not self._shutdown:
                self.__clf.connect(rdwr={'on-connect': self.pn532_recognized})
        except Exception as ex:
            logger.exception(ex)
        finally:
            logger.debug("pn532 thread ended")

    def __init__(self, input_pins, output_pins, keyboard_name, conf_pre, conf_post, *args, **kwargs):
        self.keyboard_name = keyboard_name
        self.last_key = ""
        self.last_key_time = 0
        # auslesen aus ini:
        section_name = conf_pre+'keyboard'+conf_post
        self._device = doorpi.DoorPi().config.get_string_parsed(section_name, 'device', 'tty:AMA0:pn532')
        self._InputPins = map(str.upper, input_pins)
        self._InputPairs = {}
        self.__clf = nfc.ContactlessFrontend(self._device) #init nfc-reader
        for input_pin in self._InputPins:
            self._register_EVENTS_for_pin(input_pin, __name__)
            logger.debug("__init__ (input_pin = %s)", input_pin)

        #doorpi.DoorPi().event_handler.register_event('OnFoundKnownTag', __name__)
        self._shutdown = False
        self._thread = threading.Thread(target = self.pn532_read)
        self._thread.daemon = True
        self._thread.start()
        self.register_destroy_action()

    def destroy(self):
        if self.is_destroyed: return
        logger.debug("destroy")
        self.__clf.close()
        self.__clf = None
        self._shutdown = True
        doorpi.DoorPi().event_handler.unregister_source(__name__, True)
        self.__destroyed = True

    def status_input(self, tag):
        logger.debug("status_input for tag %s", tag)
        if tag == self.last_key:
            return True
        else:
            return False

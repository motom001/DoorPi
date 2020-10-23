"""PN532 NFC keyboard module

> **Warning**: This keyboard module has not yet been extensively
> tested. Use at your own risk.

> **Warning**: The following documentation IS OUTDATED, follow it at
> your own risk.

Configuration
-------------

1. Define a new keyboard of type 'pn532'
2. Define inputPins section for that keyboard

Sample:

[keyboards]
nfcreader = pn532

[nfcreader_keyboard]
TODO
device = tty:AMA0:pn532

[nfcreader_InputPins]
1234 = **623
# calls **623 when tag-ID 1234 is scanned, logs user1 for this action
# (NOT the ID itself unless you are using debug mode)

[EVENT_OnKeyPressed_nfcreader.1234]
00 = call:**622

/TODO
That's all...

Hardware Connections
--------------------

For this keyboard we are using UART connection
Connect pn532 and Raspberry Pi as follows:
PN532   --   Raspberry Pi
VCC -- 5V
GND -- GND
RX -- GPIO 14 (TX)
TX -- GPIO 15 (RX)

IMPORTANT ---- IMPORTANT ---- IMPORTANT ---- IMPORTANT ---- IMPORTANT
TODO
you will also need the libnfc and nfcpy for this to work

1) libnfc:
   sudo apt-get install autoconf libtool libpcsclite-dev libusb-dev
   cd /home/pi
   mkdir src
   cd src
   wget https://github.com/nfc-tools/libnfc/archive/master.zip
   rename master.zip libnfc.zip
   unzip libnfc.zip
   cd libnfc --> ANPASSEN!!!!
   sudo mkdir /etc/nfc
   sudo mkdir /etc/nfc/devices.d
   sudo cp contrib/libnfc/pn532_uart_on_rpi.conf.sample /etc/nfc/devices.d/pn532_uart_on_rpi.conf
   add the line
       allow_intrusive_scan = true  <-- checken, ob das wirklich gebraucht wird
                                        und was das macht
   to file /etc/nfc/devices.d/pn532_uart_on_rpi.conf
   cd /home/pi/src/libnfc <-- anpassen
   touch NEWS
   touch README
   autoreconf -vis
   ./configure --with-drivers=pn532_uart --sysconfdir=/etc --prefix=/usr
   sudo make clean
   sudo make install all
   cd examples
   sudo ./nfc-poll
   hold a tag near the reader and you should get an output similar to this:
               SAMPLE-OUTPUT einfügen
2) nfcpy
   install following this:
        <http://nfcpy.org/latest/topics/get-started.html#installation>
   be sure that serial console is deactivated in kernel
   (cmdline.txt or raspi-config)
   test nfcpy using
       python tagtool.py --device tty:AMA0:pn532
   you should see output similar to
               SAMPLE-OUTPUT einfügen
   copy source-dir to pythons libdir:
   sudo cp -r nfc /usr/local/lib/python2.7/dist-packages/nfc   <--- CHECKEN!
/TODO
"""
import datetime
import logging
import re
import threading
from typing import Any, Optional

import nfc  # pylint: disable=import-error

import doorpi

from .abc import AbstractKeyboard

LOGGER = logging.getLogger(__name__)


class PN532Keyboard(AbstractKeyboard):
    def __init__(self, name: str) -> None:
        super().__init__(name, events=("OnKeyPressed",))
        doorpi.INSTANCE.event_handler.register_event(
            "OnTagUnknown", self._event_source
        )

        self.__device = "tty:{}:pn532".format(
            re.sub(r"^/dev/tty", "", self.config["port"])
        )
        self.__frontend = nfc.ContactlessFrontend(self.__device)

        self.__exception: Optional[Exception] = None
        self.__shutdown = False

        self.__thread = threading.Thread(target=self.pn532_read)
        self.__thread.start()

    def _deactivate(self) -> None:
        self.__shutdown = True
        self.__frontend.close()
        self.__thread.join()

    def self_check(self) -> None:
        if self.__exception is not None:
            raise RuntimeError(
                f"{self.name}: Worker died"
            ) from self.__exception
        if not self.__thread.is_alive():
            raise RuntimeError(
                f"{self.name}: Worker found dead without exception information"
            )

    def pn532_read(self) -> None:
        """The keyboard's main loop; runs as thread"""
        try:
            while not self.__shutdown:
                self.__frontend.connect(rdwr={"on-connect": self.on_connect})
        except Exception as ex:  # pylint: disable=broad-except
            self.__exception = ex

    def on_connect(self, tag: Any) -> bool:
        """Callback for when the library detects a connected tag."""
        # debounce
        now = datetime.datetime.now()
        if now - self.last_key_time <= self._bouncetime:
            return False

        self.last_key_time = now
        tag = str(tag)
        id_ = tag.split("ID=")[-1]
        LOGGER.info("%s: Tag connected: %r, ID: %r", self.name, tag, id_)
        if id_ in self._inputs:
            self._fire_event("OnKeyPressed", id_)
        else:
            doorpi.INSTANCE.event_handler(
                "OnTagUnknown",
                self._event_source,
                extra={**self.additional_info, "tag": id_},
            )
        return False


instantiate = PN532Keyboard  # pylint: disable=invalid-name

"""File I/O related stuff, i.e. the dial tone player"""

import pjsua2 as pj

from doorpi import DoorPi

from . import logger

class DialTonePlayer:
    def __init__(self, filename, loudness):
        self.__player = pj.AudioMediaPlayer()
        self.__target = None
        self.__level = loudness

        eh = DoorPi().event_handler
        eh.register_action("OnCallOutgoing_S", self.start)
        eh.register_action("OnCallConnect_S", self.stop)
        # Catch synthetic disconnects if no call was established
        eh.register_action("OnCallDisconnect_S", self.stop)

        try: self.__player.createPlayer(filename)
        except pj.Error as err:
            logger.error("Unable to create dial tone player: %s", err.info())
            self.__player = None

    def start(self):
        if self.__player is None: return

        if self.__target is None:
            self.__target = pj.Endpoint.instance().audDevManager().getPlaybackDevMedia()
        self.__player.startTransmit(self.__target)

    def stop(self):
        if self.__player is None or self.__target is None: return

        self.__player.stopTransmit(self.__target)
        self.__player.setPos(0)
        self.__target = None

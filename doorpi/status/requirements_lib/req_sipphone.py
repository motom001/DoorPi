# -*- coding: utf-8 -*-

import logging

from doorpi.sipphone import SIPPHONE_SECTION

logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)


REQUIREMENT = dict(
    fulfilled_with_one=True,
    text_description="Das SIP-Phone-Modul stellt die VoIP-Verbindungen her. Dazu verbindet es sich mit einem bestehenden SIP-Server (z.B. Asterisk oder FRITZ!Box).",
    events=[
        {"name": "OnSIPPhoneCreate", "description": "Das SIP-Phone wurde erstellt, aber noch nicht gestartet."},
        {"name": "OnSIPPhoneStart", "description": "Das SIP-Phone wurde gestartet und ist einsatzbereit."},
        {"name": "OnSIPPhoneDestroy", "description": "Das SIP-Phone wird gestoppt."},
        {"name": "OnCallOutgoing", "description": "Ein Anruf wird von DoorPi aus aufgebaut."},
        {"name": "OnCallConnect", "description": "Ein Anruf wurde verbunden (angenommen)."},
        {"name": "OnCallDisconnect", "description": "Ein Anruf wurde aufgelegt."},
        {"name": "BeforeCallIncoming", "description": "Ein externer Anruf kommt an, unabhängig von DoorPis momentanem Zustand."},
        {"name": "OnCallIncoming", "description": "Ein externer Anruf wurde angenommen."},
        {"name": "OnCallRejected", "description": "Ein externer Anruf wurde abgewiesen, weil die Nummer nicht als Administrator registriert ist."},
        {"name": "OnCallBusy", "description": "Ein externer Anruf wurde abgewiesen, weil ein anderer Anruf gerade aktiv ist."},
        {"name": "OnDTMF_<Sequenz>", "description": "Die DTMF-Sequenz <Sequenz> wurde empfangen."},
    ],
    configuration = [
        dict( section = SIPPHONE_SECTION, key = 'sipphonetyp', type = 'string', default = '', mandatory = False, description = 'Auswahl welches SIP-Phone benutzt werden soll. Derzeit wird nur "pjsua2" unterstützt.'),
        dict( section = SIPPHONE_SECTION, key = 'sipphone_server', type = 'string', default = '', mandatory = False, description = 'Wenn eine SIP-Phone Server verwendet werden soll muss dazu der Server, der Benutzername, das Passwort und der Realm angegeben werden.'),
        dict( section = SIPPHONE_SECTION, key = 'sipphone_username', type = 'string', default = '', mandatory = False, description = 'Benutzer zur Anmeldung am SIP-Phone Server'),
        dict( section = SIPPHONE_SECTION, key = 'sipphone_password', type = 'string', default = '', mandatory = False, description = 'Passwort zur Anmeldung am SIP-Phone Server'),
        dict( section = SIPPHONE_SECTION, key = 'sipphone_realm', type = 'string', default = '', mandatory = False, description = 'Realm zur Anmeldung am SIP-Phone Server (z.B. "fritz.box" bei der FritzBox)'),
        dict( section = SIPPHONE_SECTION, key = 'identity', type = 'string', default = 'DoorPi', mandatory = False, description = 'Name, der beim Telefongespräch angezeigt wird'),
        dict( section = SIPPHONE_SECTION, key = 'ua.max_calls', type = 'integer', default = '2', mandatory = False, description = 'Anzahl der max. gleichzeitigen Gespräche'),
        dict( section = SIPPHONE_SECTION, key = 'local_port', type = 'integer', default = '5060', mandatory = False, description = 'Der Port auf dem VoIP SIP Gespräche angenommen werden.'),
        dict( section = SIPPHONE_SECTION, key = 'max_call_time', type = 'integer', default = '120', mandatory = False, description = 'maximale Zeit eines Gespräches bis zum automatischen Auflegen'),
        dict( section = SIPPHONE_SECTION, key = 'call_timeout', type = 'integer', default = '15', mandatory = False, description = 'maximale Zeit die es DoorPi am Telefon klingeln lässt, bevor es wieder auflegt'),
        dict( section = SIPPHONE_SECTION, key = 'dialtone', type = 'string', default = '', mandatory = False, description = 'Pfad zur DialTone Datei. diese wird abgespielt, wenn eine Klingel betätigt wird und dient als Zeichen, dass es klingelt für den Besucher. (z.B. !BASEPATH!/doorpi/media/ShortDialTone.wav)'),
        dict( section = SIPPHONE_SECTION, key = 'dialtone_renew_every_start', type = 'boolean', default = '', mandatory = False, description = 'Der DialTone soll bei jedem Start erneut erstellt werden.'),
        dict( section = SIPPHONE_SECTION, key = 'dialtone_volume', type = 'integer', default = '35', mandatory = False, description = 'Lautstärke des DialTone, der erzeugt werden soll (in %).'),
        dict( section = SIPPHONE_SECTION, key = 'records', type = 'string', default = '', mandatory = False, description = 'Ablagepfad der aufgenommenen Gespräche (z.B. !BASEPATH!/records/!LastKey!/%Y-%m-%d_%H-%M-%S.wav)'),
        dict( section = SIPPHONE_SECTION, key = 'record_while_dialing', type = 'string', default = 'False', mandatory = False, description = 'Soll das Gespräch schon aufgenommen werden, wenn es klingelt (True) oder erst wenn die Gegenseite abgenommmen hat (False). Im Fall von verpassten Anrufen kann man aufgrund der Geräusche den Besucher eventuell erkennen.'),
        dict( section = SIPPHONE_SECTION, key = 'snapshot_path', type = 'string', default = '!Basepath!/doorpi/media/snapshots', mandatory = False, description = 'Ablagepfad der erstellten Bilder vor dem Läuten (z.B. !BASEPATH!/doorpi/media/snapshots)'),
        dict( section = SIPPHONE_SECTION, key = 'number_of_snapshots', type = 'integer', default = '10', mandatory = False, description = 'Anzahl der Bilder die gespeichert werden.')
    ],
    libraries = dict(
        pjsua2 = dict(
            text_description =      'PJSIP ist eine quelloffene Bibliothek, die Standardprotokolle wie SIP, SDP, RTP, STUN, TURN und ICE implementiert. DoorPi nutzt das zugehörige Python-Modul pjsua2, um VoIP-Verbindungen zwischen der Gegensprechanlage an der Tür und den Innenstationen bzw. Telefonen herzustellen.',
            text_installation =     'Das Modul ist im Paket ``python-pjproject`` (Arch Linux ARM) enthalten. Für Raspbian existiert derzeit kein offizielles Paket.',
            text_test =             'Der Status kann gestestet werden, indem im Python-Interpreter ``import pjsua2`` eingeben wird.',
            #text_configuration =    '',
            #configuration = [],
            text_links = {
                'Homepage Pjsua': 'http://www.pjsip.org/pjsua.htm',
                'Installationsanleitung PJSIP': 'http://trac.pjsip.org/repos/wiki/Getting-Started'
            }
        )
    )
)

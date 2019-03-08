# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from doorpi.sipphone.AbstractBaseClass import SIPPHONE_SECTION

REQUIREMENT = dict(
    fulfilled_with_one = True,
    text_description = 'Die Aufgabe eines SIP-Phones in DoorPi ist es, die Telefongespräche (VoIP-Verbindungen) herzustellen. Dazu kann das SIP-Phone entweder mit oder ohne SIP-Server (z.B. Fritz!Box oder Asterisk) zusammen arbeiten.',
    events = [
        dict( name = 'OnSipPhoneCreate', description = 'Das SIP-Phone wurde erstellt und kann gestartet werden.'),
        dict( name = 'OnSipPhoneStart', description = 'Das SIP-Phone wurde gestartet und ist jetzt einsatzbereit.'),
        dict( name = 'OnSipPhoneDestroy', description = 'Das SIP-Phone soll beendet werden.'),
        dict( name = 'OnSipPhoneRecorderCreate', description = 'Es wurde eine Recorder erstellt wurde und bereit ist Anrufe aufzuzeichnen.'),
        dict( name = 'OnSipPhoneRecorderDestroy', description = 'Es wurde ein Recorder gestoppt und es sind keine weiteren Aufnamen möglich.'),
        dict( name = 'BeforeSipPhoneMakeCall', description = 'Kurz bevor ein Gespräch von DoorPi aus gestartet wird.'),
        dict( name = 'OnSipPhoneMakeCall', description = 'Es wird ein Gespräch von DoorPi aus gestartet.'),
        dict( name = 'OnSipPhoneMakeCallFailed', description = 'Es ist ein Fehler aufgetreten, als ein Gespräch von DoorPi aus gestartet werden sollte.'),
        dict( name = 'AfterSipPhoneMakeCall', description = 'Das Gespräch wurde hergestellt und es klingelt an der Gegenstelle'),
        dict( name = 'OnSipPhoneCallTimeoutNoResponse', description = 'Das Gespräch wurde beendet, da die Gegenstelle nicht abgenommen hat (Parameter call_timeout)'),
        dict( name = 'OnSipPhoneCallTimeoutMaxCalltime', description = 'Das Gespräch wurde beendet, da das Gespräch länger als erlaubt lief (Parameter max_call_time)'),
        dict( name = 'OnPlayerCreated', description = 'Es wurde ein Player erstellt und es kann beim nächsten Anruf eine Sounddatei als Wartemusik abgespielt werden (Parameter dialtone)'),
        dict( name = 'OnCallMediaStateChange', description = 'Die Nutzung der Ein- un Ausgabegeräte (Audio und Video) hat sich geändert.'),
        dict( name = 'OnMediaRequired', description = 'Es existiert ein Call und es wird das Media-Gerät benötigt. Kann z.B. genutzt werden um Verstärker zu aktivieren.'),
        dict( name = 'OnMediaNotRequired', description = 'Es existiert kein Call (mehr) und es wird das Media-Gerät nicht (mehr) benötigt. Kann z.B. genutzt werden um Verstärker zu deaktivieren.'),
        dict( name = 'OnCallStateChange', description = 'Der Status eines Anrufs hat sich verändert'),
        dict( name = 'OnCallStateConnect', description = 'Der Stauts eines Gespräches ist jetzt wieder auf verbunden (Connected, Resuming oder Updating)'),
        dict( name = 'AfterCallStateConnect', description = 'Das Gespräch wurde aufgebaut, die Media-Verbindung besteht'),
        dict( name = 'OnCallStateDisconnect', description = 'Das Gespräch wurde beendet'),
        dict( name = 'AfterCallStateDisconnect', description = '[nicht mehr belegt]'),
        dict( name = 'OnCallStateDismissed', description = 'Es sollte angerufen werden, jedoch sit die Gegenstelle besetzt.'),
        dict( name = 'OnCallStateReject', description = 'Das Gespräch wurde von der Gegenstelle abgelehnt.'),
        dict( name = 'OnCallStart', description = 'Initialisierung der Call-Back Funktionen'),
        dict( name = 'OnDTMF', description = 'Es wurden DTMF-Signale empfangen. Es wird zusätzlich ein Event in der Form ´OnDTMF_"#"´ ausglöst (wenn # gedrückt wurde), wenn das empfangene DTMF-Signal in der Config definiert und somit erwartet wurde.'),
        dict( name = 'BeforeCallIncoming', description = 'Wenn ein Gespräch ankommt, und noch nicht weiter bearbeitet wurde'),
        dict( name = 'OnCallReconnect', description = 'Wenn bereits ein Gespräch exisitert und ein Gespräch zur gleichen Nummer erneut aufgebaut wird.'),
        dict( name = 'AfterCallReconnect', description = 'Nachdem bereits ein Gespräch exisitert hat und ein Gespräch zur gleichen Nummer erneut aufgebaut wurde.'),
        dict( name = 'OnCallBusy', description = 'Wenn DoorPi gerade beschäftigt ist und kein weitere Gespräch annehmen kann.'),
        dict( name = 'AfterCallBusy', description = 'Nachdem DoorPi ein ankommendes Gespräch abgelehnt hat, da bereits ein anderes Gespräch geführt wird.'),
        dict( name = 'OnCallIncoming', description = 'Bevor ein ankommendes Gespräch angenommen wird (ist eine Admin-Nummer)'),
        dict( name = 'AfterCallIncoming', description = 'Nachdem ein ankommendes Gespräch angenommen wurde (ist eine Admin-Nummer)'),
        dict( name = 'OnCallReject', description = 'Bevor ein ankommendes Gespräch abgelehnt wird (keine Admin-Nummer)'),
        dict( name = 'AfterCallReject', description = 'Nachdem ein ankommendes Gespräch abgelehnt wurde (keine Admin-Nummer)'),
        dict( name = 'OnPlayerStarted', description = 'Die Wiedergabe vom DialTone wurde gestartet'),
        dict( name = 'OnPlayerStopped', description = 'Die Wiedergabe vom DialTone wurde gestoppt'),
        dict( name = 'OnRecorderStarted', description = 'Die Aufnahme des Gespräches wurde gestartet'),
        dict( name = 'OnRecorderStopped', description = 'Die Aufnahme des Gespräches wurde gestoppt'),
        dict( name = 'OnRecorderCreated', description = 'Es wurde eine Recorder erstellt wurde und bereit ist Anrufe aufzuzeichnen.')
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

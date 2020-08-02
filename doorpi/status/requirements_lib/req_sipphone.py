from doorpi.sipphone import SIPPHONE_SECTION


REQUIREMENT = dict(
    fulfilled_with_one=True,
    text_description="Das SIP-Phone-Modul stellt die VoIP-Verbindungen her. Dazu verbindet es sich mit einem bestehenden SIP-Server (z.B. Asterisk oder FRITZ!Box).",
    libraries=dict(
        pjsua2=dict(
            text_description='PJSIP ist eine quelloffene Bibliothek, die Standardprotokolle wie SIP, SDP, RTP, STUN, TURN und ICE implementiert. DoorPi nutzt das zugehörige Python-Modul pjsua2, um VoIP-Verbindungen zwischen der Gegensprechanlage an der Tür und den Innenstationen bzw. Telefonen herzustellen.',
            text_installation='Das Modul ist im Paket ``python-pjproject`` (Arch Linux ARM) enthalten. Für Raspbian existiert derzeit kein offizielles Paket.',
            text_test='Der Status kann gestestet werden, indem im Python-Interpreter ``import pjsua2`` eingeben wird.',
            text_links={
                'Homepage Pjsua': 'http://www.pjsip.org/pjsua.htm',
                'Installationsanleitung PJSIP': 'http://trac.pjsip.org/repos/wiki/Getting-Started'
            }
        )
    )
)

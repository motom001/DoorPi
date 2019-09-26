from doorpi.status.webserver import DOORPIWEB_SECTION, CONF_AREA


REQUIREMENT = dict(
    fulfilled_with_one=False,
    text_description=f'''Der Webserver ist Kontroll- und Konfigurationsoberfläche sowie die
Schnittstelle per Webservice.  Es können Dateien angefragt werden (z.B.
``index.html``), die aus dem Dateisystem geladen werden (reale
Resourcen).  Genausogut können aber auch Status Abfragen oder Control
Kommandos verarbeitet werden (virtuelle Resourcen).

Der Benutzer wird vorranging nur reale Resourcen aufrufen, die sich den
angezeigten Status über virtuelle Resourcen "nachladen".

Wenn es um eine Weboberfläche geht, dann sollte diese auch abgesichert
sein.  Dazu gibt es Nutzer (User) die in Gruppen (Groups)
zusammengefasst sind.  Diesen Groups sind  Bereiche (AREA) zugeteilt,
die lesend oder schreibend genutzt werden können.  Die Bereiche (AREA)
sind virtuelle und reale Ressourcen, die sich speziell an der URL
unterscheiden (daher kam auch die Idee, es in Bereiche einzuteilen).
Die Bestandteile eines Bereiches werden mittels RegEx definiert.

Zuordnung in der Sektion User ist::

    Benutzername = Passwort

Bei der Group Sektion ist es::

    GroupName = Benutzername1,Benutzername2,...

Dann gibt es die beiden Sektionen WritePermission und ReadPermission
mit der Zuordnung::

    GroupName = AreaName

Ganz unten gibt es dann beliebig viele Areas mit unterschiedlichen
Namen.  Jeder Area sind RegEx zugeordnet, die gegen die URL geprüft
werden.  Eine Sonderform ist die AREA_public.  Diese fasst alle
Ressourcen zusammen, die von jedem eingesehen werden dürfen, da es sich
hierbei um Javascript, CSS und ähnliche Dateien handelt.

Beispiel::

    [{DOORPIWEB_SECTION}]
    # alle Resourcen, die jeder sehen darf, auch wenn er sich nicht
    # authentifiziert hat
    public = {CONF_AREA.format(area="public")}

    [User]
    # Benutzer door mit dem Passwort pi
    door = pi

    [Group]
    # Benutzer door ist Mitglied der Gruppe administrator
    administrator = door

    [WritePermission]
    # Gruppe administrator darf schreibend auf die Resourcen dashboard
    # zugreifen (Sektion "{CONF_AREA.format(area="dashboard")}")
    administrator = dashboard

    [ReadPermission]
    # Gruppe administrator darf lesend auf die Resourcen status
    # (Sektion "{CONF_AREA.format(area="status")}") und help
    # (Sektion "{CONF_AREA.format(area="help")}") zugreifen
    administrator = status, help

    [{CONF_AREA.format(area="status")}]
    # alle URLs die mit "/status" übereinstimmen (Parameter der URL
    # sind dabei egal - so ist z.B. "/status?output=plain" möglich)
    /status
    /mirror

    [{CONF_AREA.format(area="dashboard")}]
    /dashboard/pages/.*html

    [{CONF_AREA.format(area="help")}]
    /help/.*

    [{CONF_AREA.format(area="public")}]
    /dashboard/bower_components/.*
    /dashboard/dist/.*
    /dashboard/js/.*
    /dashboard/less/.*
    /login.html
    /favicon.ico
''',
    events=[
        dict(name='OnWebServerStart', description='Der Webserver ist gestartet. Somit stehen die Webservices und die Weboberfläche zur Verfügung. Standardmäßig wird Port 80 benutzt (Parameter ip und port)'),
        dict(name='OnWebServerStop', description='Der Webserver soll gestoppt werden. Ab diesem Zeitpunkt werden keine neuen Anfragen bearbeitet.'),
        dict(name='WebServerCreateNewSession', description='Es hat sich ein Nutzer angemeldet, der seit dem Start von DoorPi noch angemeldet war.'),
        dict(name='WebServerAuthUnknownUser', description='Es wurde versucht sich mit einem Benutzer anzumelden, der nicht bekannt ist.'),
        dict(name='WebServerAuthWrongPassword', description='Für einen existierenden Benutzer wurde ein falsches Passwort übermittelt.'),
        dict(name='OnWebServerRequest', description='Es wurde eine Anfrage an den Webserver gestellt - dabei ist egal ob per GET oder POST'),
        dict(name='OnWebServerRequestGet', description='Es wurde eine GET-Anfrage an den Webserver gestellt'),
        dict(name='OnWebServerRequestPost', description='Es wurde eine POST-Anfrage an den Webserver gestellt'),
        dict(name='OnWebServerVirtualResource', description='Es wurde eine Anfrage an den Webserver gestellt, die auf eine virtuelle Resource zeigt (z.B. Webservice erfordert JSON-String)'),
        dict(name='OnWebServerRealResource', description='Es wurde eine Anfrage an den Webserver gestellt, die auf eine reale Resource zeigt (z.B. User ruft das Dashboard auf)'),
    ],
    configuration=[
        dict(section=DOORPIWEB_SECTION, key='ip', type='string', default='', mandatory=False, description='IP-Adresse an die der Webserver gebunden werden soll (leer=alle)'),
        dict(section=DOORPIWEB_SECTION, key='port', type='integer', default='80', mandatory=False, description='Der Port auf den der Webserver lauschen soll. Achtung - kann bei anderen installierten Webservern zu Kollisionen führen!'),
        dict(section=DOORPIWEB_SECTION, key='www', type='string', default='!BASEPATH!/../DoorPiWeb', mandatory=False, description='Der Ort, an dem reale Ressourcen (HTML, CSS, JS) installiert wurden.'),
        dict(section=DOORPIWEB_SECTION, key='indexfile', type='string', default='index.html', mandatory=False, description='[nicht eingebunden]'),
        dict(section=DOORPIWEB_SECTION, key='public', type='string', default='AREA_public', mandatory=False, description='Der Name der Public Sektion mit allen öffentlich aufrufbaren Resourcen (z.B. JS- und CSS-Dateien fürs Dashbaord)'),
        dict(section='User', key='*', type='string', default='', mandatory=False, description='Sektion, die alle Benutzer beinhaltet - in der Form [username]=[password]'),
        dict(section='Group', key='*', type='string', default='', mandatory=False, description='Sektion die alle Gruppen und deren Mitglieder beinhaltet. Mehrere Nutzer werden durch ein Komma getrennt - in der Form [groupname]=[user1],[user2],...'),
        dict(section='ReadPermission', key='*', type='string', default='', mandatory=False, description=''),
        dict(section='WritePermission', key='*', type='string', default='', mandatory=False, description=''),
        dict(section=CONF_AREA.format(area='*'), key='*', type='string', default='', mandatory=False, description='')
    ],
    libraries={
        'http.server': dict(
            text_description='Das Python-Modul http.server ist mit der Klasse HTTPServer die Grundlage für jeden Webserver.',
            text_installation='Eine Installation ist nicht nötig, da es sich hierbei um ein Python-Standard-Modul handelt.',
            auto_install=False,
            text_test='Der Status kann gestestet werden, indem im Python-Interpreter ``import http.server`` eingeben wird.',
            text_links={
                'docs.python.org': 'https://docs.python.org/2.7/library/basehttpserver.html'
            }
        ),
        'urllib': dict(
            text_description='Das Python-Modul urllib wird vom Webserver benötigt, um Anfragen zu verarbeiten.',
            text_installation='Eine Installation ist nicht nötig, da es sich hierbei um ein Python-Standard-Modul handelt.',
            auto_install=False,
            text_test='Der Status kann gestestet werden, indem im Python-Interpreter ``import urllib`` eingeben wird.',
            text_links={
                'docs.python.org': 'https://docs.python.org/2.7/library/urllib2.html'
            }
        ),
        'mimetypes': dict(
            text_description='Das Python-Modul mimetypes ermöglicht die Bestimmung des MIME-Typs anhand von Dateiendungen. Wichtig ist das bei der Entscheidung um Platzhalter innerhalb dieser Datei verarbeitet werden sollen (HTML-Template) oder nicht (z.B. Bilddatei).',
            text_installation='Eine Installation ist nicht nötig, da es sich hierbei um ein Python-Standard-Modul handelt.',
            auto_install=False,
            text_test='Der Status kann gestestet werden, indem im Python-Interpreter ``import mimetypes`` eingeben wird.',
            text_links={
                'docs.python.org': 'https://docs.python.org/2.7/library/mimetypes.html',
                'MIME-Typen': 'http://wiki.selfhtml.org/wiki/Referenz:MIME-Typen',
                'Media Types auf iana.org': 'http://www.iana.org/assignments/media-types/media-types.xhtml',
                'RFC2616  - Abschnitt 14.17': 'https://tools.ietf.org/html/rfc2616#section-14.17'
            }
        ),
        'docutils.core': dict(
            text_description='Die docutils werden genutzt, um diese Informationsseiten darzustellen.',
            text_installation='Das Modul ist im Paket ``python3-docutils`` (Raspbian) bzw. ``python-docutils`` (Arch Linux ARM) enthalten.',
            auto_install=False,
            text_test='Der Status kann getestet werden, indem im Python-Interpreter ``import docutils.core`` eingegeben wird.',
            text_links={
                'Sourceforge': 'http://docutils.sourceforge.net/',
                'rst Format-Einführung': 'http://docutils.sourceforge.net/docs/user/rst/quickstart.html'
            }
        )
    }
)

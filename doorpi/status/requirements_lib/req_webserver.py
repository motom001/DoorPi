import textwrap

REQUIREMENT = {
    "fulfilled_with_one": False,
    "text_description": textwrap.dedent("""\
        Der Webserver ist Kontroll- und Konfigurationsoberfläche sowie die
        Schnittstelle per Webservice.  Es können Dateien angefragt werden (z.B.
        ``index.html``), die aus dem Dateisystem geladen werden (reale
        Resourcen).  Genausogut können aber auch Statusabfragen oder Befehle
        verarbeitet werden (virtuelle Resourcen).

        Der Benutzer wird vorranging nur reale Resourcen aufrufen, die sich den
        angezeigten Status über virtuelle Resourcen "nachladen".

        Wenn es um eine Weboberfläche geht, dann sollte diese auch abgesichert
        sein.  Dazu gibt es Nutzer (User) die in Gruppen (Groups)
        zusammengefasst sind.  Diesen Groups sind  Bereiche (Areas) zugeteilt,
        die lesend oder schreibend genutzt werden können.  Die Areas sind
        virtuelle und reale Ressourcen, die sich speziell an der URL
        unterscheiden (daher kam auch die Idee, es in Bereiche einzuteilen).
        Die Bestandteile eines Bereiches werden mittels RegEx definiert.

        Zuordnung in der Sektion ``[web.users]`` ist::

            [web.users]
            "Benutzername" = "Passwort"

        Bei der ``[web.groups]``\\ -Sektion ist es::

            [web.groups]
            "GroupName" = [
                "Benutzername1",
                "Benutzername2",
                ...
            ]

        Dazu gibt es die beiden Sektionen ``[web.writeaccess]`` und
        ``[web.readaccess]`` mit der Zuordnung::

            "GroupName" = [
                "AreaName",
                ...
            ]

        Unter ``[web.areas]`` gibt es dann beliebig viele Areas mit
        unterschiedlichen Namen.  Jeder Area sind RegEx zugeordnet, die gegen
        die URL geprüft werden.  Eine Sonderform ist die Area "public".  Diese
        ist ohne Authentifizierung abrufbar und gedacht für statische Ressourcen
        wie JavaScript und CSS.

        Beispiel::

            [web.users]
            door = "pi"

            [web.groups]
            # Benutzer door ist Mitglied der Gruppe "administrator"
            administrator = door

            [web.writeaccess]
            # Gruppe administrator darf schreibend auf die Resourcen dashboard
            # zugreifen (Sektion "{CONF_AREA.format(area="dashboard")}")
            administrator = ["dashboard"]

            [web.readaccess]
            # Gruppe administrator darf lesend auf die Resourcen status
            # (Sektion "{CONF_AREA.format(area="status")}") und help
            # (Sektion "{CONF_AREA.format(area="help")}") zugreifen
            administrator = status, help

            [web.areas]
            help = [
                # alle URLs die mit "/status" übereinstimmen (Parameter der URL
                # sind dabei egal - so ist z.B. "/status?output=plain" möglich)
                "/status",
                "/mirror",
            ]
            dashboard = [
                "/dashboard/pages/.*\\.html",
            ]
            help = [
                "/help/.*",
            ]
            public = [
                "/dashboard/bower_components/.*",
                "/dashboard/dist/.*",
                "/dashboard/js/.*",
                "/dashboard/less/.*",
                "/login.html",
                "/favicon.ico",
            ]
            """),
    "libraries": {
        "http.server": {
            "text_description": (
                "Das Python-Modul ``http.server`` ist mit der Klasse"
                " ``HTTPServer`` die Grundlage für den DoorPi-Webserver."),
            "text_installation": (
                "Eine Installation ist nicht nötig, da es sich hierbei um ein"
                " Python-Standard-Modul handelt."),
            "auto_install": False,
            "text_test": (
                "Der Status kann gestestet werden, indem im Python-Interpreter"
                " ``import http.server`` eingeben wird."),
            "text_links": {
                "docs.python.org": (
                    "https://docs.python.org/library/basehttpserver.html"),
            }
        },
        "urllib": {
            "text_description": (
                "Das Python-Modul ``urllib`` wird vom Webserver benötigt, um"
                " Anfragen zu verarbeiten."),
            "text_installation": (
                "Eine Installation ist nicht nötig, da es sich hierbei um ein"
                " Python-Standard-Modul handelt."),
            "auto_install": False,
            "text_test": (
                "Der Status kann gestestet werden, indem im Python-Interpreter"
                " ``import urllib`` eingeben wird."),
            "text_links": {
                "docs.python.org": (
                    "https://docs.python.org/library/urllib2.html"),
            },
        },
        "mimetypes": {
            "text_description": (
                "Das Python-Modul ``mimetypes`` ermöglicht die Bestimmung des"
                " MIME-Typs anhand von Dateiendungen.  Wichtig ist das bei der"
                " Entscheidung, ob Platzhalter innerhalb dieser Datei"
                " verarbeitet werden sollen (HTML-Template) oder nicht"
                " (z.B. Bilddateien)."),
            "text_installation": (
                "Eine Installation ist nicht nötig, da es sich hierbei um ein"
                " Python-Standard-Modul handelt."),
            "auto_install": False,
            "text_test": (
                "Der Status kann gestestet werden, indem im Python-Interpreter"
                " ``import mimetypes`` eingeben wird."),
            "text_links": {
                "docs.python.org":(
                    "https://docs.python.org/library/mimetypes.html"),
                "MIME-Typen": (
                    "http://wiki.selfhtml.org/wiki/Referenz:MIME-Typen"),
                "Media Types auf iana.org": (
                    "http://www.iana.org/assignments"
                    "/media-types/media-types.xhtml"),
                "RFC2616  - Abschnitt 14.17": (
                    "https://tools.ietf.org/html/rfc2616#section-14.17"),
            },
        },
        "docutils.core": {
            "text_description": (
                "Die ``docutils`` werden genutzt, um diese"
                " Informationsseiten darzustellen."),
            "text_installation": (
                "Das Modul ist im Paket ``python3-docutils`` (Raspbian) bzw."
                " ``python-docutils`` (Arch Linux ARM) enthalten."),
            "auto_install": False,
            "text_test": (
                "Der Status kann getestet werden, indem im Python-Interpreter "
                " ``import docutils.core`` eingegeben wird."),
            "text_links": {
                "Sourceforge": "http://docutils.sourceforge.net/",
                "rst Format-Einführung": (
                    "http://docutils.sourceforge.net/docs/user"
                    "/rst/quickstart.html"),
            },
        },
    },
}

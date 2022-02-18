import textwrap

REQUIREMENT = {
    "text_description": textwrap.dedent(
        """\
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
            """
    ),
}

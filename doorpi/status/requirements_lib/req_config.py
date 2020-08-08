REQUIREMENT = dict(
    fulfilled_with_one=True,
    libraries=dict(
        configparser=dict(
            text_description='Das Config-Modul wird benötigt, um alle Einstellungen in einer Datei abspeichern und später wieder laden zu können.',
            text_installation='Eine Installation ist nicht nötig, da es sich hierbei um ein Python-Standard-Modul handelt.',
            auto_install=False,
            text_test='Der Status kann gestestet werden, indem im Python-Interpreter ``import configparser`` eingeben wird.',
            text_configuration=\
'''Eine Konfiguration als Eintrag in der Konfigurationsdatei hat
logischerweise keinen Sinn.  Deshalb kann die zu nutzende Config-Datei
als Parameter (``--configfile``) beim DoorPi Start mitgegeben werden.

Beispiel::

    doorpi_cli --configfile /etc/doorpi/doorpi.ini

Wird der Parameter nicht angegeben, wird die Datei von einem
Standardpfad geladen.  Dieser Pfad hängt davon ab, wo DoorPi
installiert wurde:

- Wurde es systemweit unterhalb von ``/usr`` installiert (bspw. mittels
  AUR-Paket), liegt die Standarddatei in::

    /etc/doorpi/doorpi.ini
- Wurde DoorPi systemweit unterhalb von ``/usr/local`` installiert,
  liegt die Standarddatei in::

    /usr/local/etc/doorpi/doorpi.ini
- Wurde das Programm in einem Python Virtualenv installiert, liegt die
  Datei innerhalb des Virtualenvs::

    $VIRTUAL_ENV/etc/doorpi/doorpi.ini

Sollte die Datei nicht existieren, wird DoorPi mit seinen eingebauten
Standardwerten gestartet.
''',
            text_links={
                'docs.python.org': 'https://docs.python.org/2.7/library/configparser.html'
            }
        )
    )
)

import textwrap

REQUIREMENT = {
    "fulfilled_with_one": False,
    "text_description": (
        "Alle Module vom Bereich System sind für den Betrieb von DoorPi an"
        " verschiedenen Stellen zwingend nötig."),
    "libraries": {
        "importlib": {
            "text_description": textwrap.dedent("""\
                Das Python-Modul ``importlib`` wird zum dynamischen Laden von
                Dateien als Modul genutzt.  So sind z.B. alle Keyboards jeweils
                als eigene Datei abgelegt, die anhand des Dateinamens (= Typ des
                Keyboards) geladen werden, wenn diese auch wirklich benötigt
                werden.
                """),
            "text_installation": (
                "Eine Installation ist nicht nötig, da es sich hierbei um ein"
                " Python-Standard-Modul handelt."),
            "auto_install": False,
            "text_test": (
                "Der Status kann gestestet werden, indem im Python-Interpreter"
                " ``import importlib`` eingeben wird."),
            "text_links": {
                "docs.python.org": (
                    "https://docs.python.org/library/importlib.html"),
            },
        },
        "os": {
            "text_description": (
                "Das Python-Modul ``os`` gibt DoorPi die Möglichkeit, mit dem"
                " System zu kommunizieren, auf dem es läuft."),
            "text_installation": (
                "Eine Installation ist nicht nötig, da es sich hierbei um ein"
                " Python-Standard-Modul handelt."),
            "auto_install": False,
            "text_test": (
                "Der Status kann gestestet werden, indem im Python-Interpreter"
                " ``import os`` eingeben wird."),
            "text_links": {
                "docs.python.org": "https://docs.python.org/library/os.html",
            },
        },
        "logging": {
            "text_description": textwrap.dedent("""\
                Das Python-Modul ``logging`` wird in DoorPi genutzt um die
                Log-Ausgaben, also die Status-Meldungen von DoorPi, an die
                gewünschten Stellen zu schreiben.  Im Anwendungsmodus wird keine
                Log-Datei geschrieben, sondern nur die Log-Ausgabe am Bildschrim
                angezeigt.  Im Daemon-Modus allerdings wird eine Log-Datei
                geschrieben (`/var/log/doorpi/doorpi.log`__).  Die maximale
                Größe der Logdatei ist auf 50000 Bytes festgelegt.  Danach wird
                die Log-Datei "rotiert" (umbenannt) und eine neue geschrieben.
                Es gibt jedoch max. die 10 letzten Log-Dateien - alle älteren
                werden verworfen.

                __ https://github.com/motom001/DoorPi/blob/master/doorpi/main.py#L15
                """),
            "text_installation": (
                "Eine Installation ist nicht nötig, da es sich hierbei um ein"
                " Python-Standard-Modul handelt."),
            "auto_install": False,
            "text_test": (
                "Der Status kann gestestet werden, indem im Python-Interpreter"
                " ``import importlib`` eingeben wird."),
            "text_links": {
                "docs.python.org": (
                    "https://docs.python.org/library/logging.html"),
            },
        },
        "re": {
            "text_description": (
                "Das Python-Modul ``re`` wird für reguläre Ausdrücke genutzt."),
            "text_installation": (
                "Eine Installation ist nicht nötig, da es sich hierbei um ein"
                " Python-Standard-Modul handelt."),
            "auto_install": False,
            "text_test": (
                "Der Status kann gestestet werden, indem im Python-Interpreter"
                " ``import re`` eingeben wird."),
            "text_links": {
                "docs.python.org": "https://docs.python.org/library/re.html",
            },
        },
        "json": {
            "text_description": (
                "Das Python-Modul ``json`` ermöglicht DoorPi, die internen"
                " Objekte in lesbare JSON-Strings umzuwandeln und später"
                " auszugeben.  Vor allem im Bereich des Webservers werden so"
                " die Inhalte aufbereitet."),
            "text_installation": (
                "Eine Installation ist nicht nötig, da es sich hierbei um ein"
                " Python-Standard-Modul handelt."),
            "auto_install": False,
            "text_test": (
                "Der Status kann gestestet werden, indem im Python-Interpreter"
                " ``import json`` eingeben wird."),
            "text_links": {
                "docs.python.org": "https://docs.python.org/library/json.html",
            },
        },
        "time": {
            "text_description": (
                "Das Python-Modul ``time`` bietet die Funktion ``sleep``,"
                " die als Action sowie an einigen anderen Stellen innerhalb"
                " von DoorPi genutzt wird."),
            "text_installation": (
                "Eine Installation ist nicht nötig, da es sich hierbei um ein"
                " Python-Standard-Modul handelt."),
            "auto_install": False,
            "text_test": (
                "Der Status kann gestestet werden, indem im Python-Interpreter"
                " ``import time`` eingeben wird."),
            "text_links": {
                "docs.python.org": "https://docs.python.org/library/time.html",
            },
        },
        "sys": {
            "text_description": (
                "Das Python-Modul ``sys`` gibt DoorPi die Möglichkeit mit dem"
                " System zu kommunizieren, auf dem es läuft."),
            "text_installation": (
                "Eine Installation ist nicht nötig, da es sich hierbei um ein"
                " Python-Standard-Modul handelt."),
            "auto_install": False,
            "text_test": (
                "Der Status kann gestestet werden, indem im Python-Interpreter"
                " ``import sys`` eingeben wird."),
            "text_links": {
                "docs.python.org": "https://docs.python.org/library/sys.html",
            },
        },
        "argparse": {
            "text_description": (
                "Das Python-Modul ``argparse`` wird genutzt, um die Parameter"
                "beim DoorPi-Start auszuwerten."),
            "text_installation": (
                "Eine Installation ist nicht nötig, da es sich hierbei um ein"
                " Python-Standard-Modul handelt."),
            "auto_install": False,
            "text_test": (
                "Der Status kann gestestet werden, indem im Python-Interpreter"
                " ``import argparse`` eingeben wird."),
            "text_links": {
                "docs.python.org": (
                    "https://docs.python.org/library/argparse.html"),
            },
        },
        "datetime": {
            "text_description": (
                "Das Python-Modul ``datetime`` wird genutzt,"
                " um Zeitstempel zu erzeugen."),
            "text_installation": (
                "Eine Installation ist nicht nötig, da es sich hierbei um ein"
                " Python-Standard-Modul handelt."),
            "auto_install": False,
            "text_test": (
                "Der Status kann gestestet werden, indem im Python-Interpreter"
                " ``import datetime`` eingeben wird."),
            "text_links": {
                "docs.python.org": (
                    "https://docs.python.org/library/datetime.html"),
            },
        },
        "cgi": {
            "text_description": (
                "Das Python-Modul ``cgi`` wird unter anderem zum Parsen von"
                " POST-Anfragen beim Webserver benötigt."),
            "text_installation": (
                "Eine Installation ist nicht nötig, da es sich hierbei um ein"
                " Python-Standard-Modul handelt."),
            "auto_install": False,
            "text_test": (
                "Der Status kann gestestet werden, indem im Python-Interpreter"
                " ``import cgi`` eingeben wird."),
            "text_links": {
                "docs.python.org": "https://docs.python.org/library/cgi.html",
            },
        },
        "resource": {
            "text_description": (
                "Das Python-Modul ``resource`` ermöglicht Abfragen des"
                " System-Zustands, auf dem DoorPi läuft."),
            "text_installation": (
                "Eine Installation ist nicht nötig, da es sich hierbei um ein"
                " Python-Standard-Modul handelt."),
            "auto_install": False,
            "text_test": (
                "Der Status kann gestestet werden, indem im Python-Interpreter"
                " ``import resource`` eingeben wird."),
            "text_links": {
                "docs.python.org": (
                    "https://docs.python.org/library/resource.html"),
            },
        },
        "random": {
            "text_description": (
                "Das Python-Modul ``random`` ermöglicht die Erstellung von"
                " Zufallszahlen und -zeichenketten (z.B. Event-IDs)."),
            "text_installation": (
                "Eine Installation ist nicht nötig, da es sich hierbei um ein"
                " Python-Standard-Modul handelt."),
            "auto_install": False,
            "text_test": (
                "Der Status kann gestestet werden, indem im Python-Interpreter"
                " ``import random`` eingeben wird."),
            "text_links": {
                "docs.python.org": (
                    "https://docs.python.org/library/random.html"),
            },
        },
        "string": {
            "text_description": (
                "Das Python-Modul ``string`` wird zur Manipulation von"
                " Zeichenketten genutzt."),
            "text_installation": (
                "Eine Installation ist nicht nötig, da es sich hierbei um ein"
                " Python-Standard-Modul handelt."),
            "auto_install": False,
            "text_test": (
                "Der Status kann gestestet werden, indem im Python-Interpreter"
                " ``import string`` eingeben wird."),
            "text_links": {
                "docs.python.org": (
                    "https://docs.python.org/library/string.html"),
            },
        },
    },
}

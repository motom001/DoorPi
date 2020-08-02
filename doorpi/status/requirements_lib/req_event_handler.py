REQUIREMENT = dict(
    fulfilled_with_one=False,
    text_description='''
Der Event-Handler ist das Herz-Stück von DoorPi und die Vermittlerstelle zwischen den Events und Actions.
Bei ihm müssen sich alle Module anmelden, die Events abfeuern können oder Actions bei bestimmten Events ausgelöst bekommen wollen.
Jedes Event für sich wird seriell (eins nach dem anderen) abgearbeitet. Mehrere Events werden parallel (alle auf einmal) ausgeführt.
Damit das parallele Ausführen von Actions möglich wird, arbeitet der Event-Handler mit Threads.

Die ausgelösten Events werden in einer Datenbank (SQLite) gespeichert und können z.B. in der Weboberfläche ausgewertet werden.
''',
    libraries=dict(
        threading=dict(
            text_description='Grundmodul für das Threading, also die parallele Ausführung von Events.',
            text_installation='Eine Installation ist nicht nötig, da es sich hierbei um ein Python-Standard-Modul handelt.',
            auto_install=False,
            text_test='Der Status kann gestestet werden, indem im Python-Interpreter ``import threading`` eingeben wird.',
            text_links={
                'docs.python.org': 'https://docs.python.org/2.7/library/threading.html'
            }
        ),
        inspect=dict(
            text_description='Das Python-Modul inspect kann den Zustand eines laufenden Programms analysieren und Funktionen bzw. Objekte auswerten. Das wird z.B. bei der Parameterbestimmung der Actions benötigt um die Schnittstelle Event-Handler zu Action so abstrakt wie möglich halten zu können.',
            text_installation='Eine Installation ist nicht nötig, da es sich hierbei um ein Python-Standard-Modul handelt.',
            auto_install=False,
            text_test='Der Status kann gestestet werden, indem im Python-Interpreter ``import inspect`` eingeben wird.',
            text_links={
                'docs.python.org': 'https://docs.python.org/2.7/library/inspect.html'
            }
        ),
        sqlite3=dict(
            text_warning='',
            text_description='SQLite is a C library that provides a lightweight disk-based database that doesn’t require a separate server process and allows accessing the database using a nonstandard variant of the SQL query language. Some applications can use SQLite for internal data storage. It’s also possible to prototype an application using SQLite and then port the code to a larger database such as PostgreSQL or Oracle.',
            text_installation='Eine Installation ist nicht nötig, da es sich hierbei um ein Python-Standard-Modul handelt.',
            auto_install=False,
            text_test='Der Status kann gestestet werden, indem im Python-Interpreter ``import sqlite3`` eingeben wird.',
            text_links={
                'docs.python.org': 'https://docs.python.org/2.7/library/sqlite3.html'
            }
        )
    )
)

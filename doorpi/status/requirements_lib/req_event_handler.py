import textwrap

REQUIREMENT = {
    "text_description": textwrap.dedent("""\
        Der Event-Handler ist das Herzstück von DoorPi und die Vermittlerstelle
        zwischen den Events und Actions.  Bei ihm müssen sich alle Module
        anmelden, die Events abfeuern können oder Actions bei bestimmten Events
        ausgelöst bekommen wollen.

        Jedes Event für sich wird seriell (eins nach dem anderen) abgearbeitet.
        Mehrere Events werden parallel (alle auf einmal) ausgeführt.  Damit das
        parallele Ausführen von Actions möglich wird, arbeitet der Event-Handler
        mit Threads.

        Die ausgelösten Events werden in einer SQLite-Datenbank gespeichert und
        können z.B. in der Weboberfläche ausgewertet werden."""),
}

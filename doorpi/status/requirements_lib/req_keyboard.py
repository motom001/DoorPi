import textwrap

REQUIREMENT = {
    "text_description": textwrap.dedent("""\
        Die Aufgabe von einem Keyboard innerhalb von DoorPi ist es, Eingaben
        und Ausgaben zu steuern. Keyboard bezieht sich dabei nicht auf die
        Tastatur, sondern auf ein Brett mit Knöpfen und LEDs.  DoorPi ist in der
        Lage, mehrere Keyboards gleichzeitig zu verwalten. Dazu muss in der
        Konfiguration zuerst eine Zuordnung getroffen werden, welchen frei
        ausgedachten, aber eindeutigen Namen das Keyboard bekommmt
        (``KeyboardName``) und von welchem Typ das Keyboard ist.  Diese
        Zuordnung findet in einer Konfigurations-Sektion "keyboards" statt.
        Danach kann jedes Keyboard drei weitere Sektionen besitzen:

        1. allgemeine und Keyboard-spezifische Konfigurationsparameter
           (Sektionsname ``keyboard_settings_[KeyboardName]``)
        2. Auflistung der InputPins (Sektionsname
           ``keyboard_input_[KeyboardName]``), wobei Pin auch eine Zeichenkette
           sein kann wie im Beispiel vom RFID-Reader.
        3. Auflistung der OutputPins (Sektionsname
           ``keyboard_output_[KeyboardName]``) mit Pinnummer und sprechendem
           Namen

        Der sprechende Name muss eindeutig sein und wird später genutzt, um die
        Pins in Actions anzusprechen.

        Beispiel (alles nach einem # sind Kommentare)::

            virtuelles = filesystem
            rfid = rdm6300

            [keyboard_settings_virtuelles]
            # Pfad, in dem dann die Input-Dateien zu finden sind
            base_path_input = !BASEPATH!/keyboards/virtuelles/inputpins
            # Pfad, in dem dann die Output-Dateien zu finden sind
            base_path_output = !BASEPATH!/keyboards/virtuelles/outputpins
            # Ausgangszustand der Eingabe-Datei soll wiederhergestellt werden,
            # wenn Signal erkannt wurde
            reset_input = true

            [keyboard_input_virtuelles]
            # Wenn diese Datei eine '1' beinhaltet, dann soll ein Ausgang mit
            # dem Namen tueroeffner gesteuert werden
            klingel = out:tueroeffner:0,1,3

            [keyboard_output_virtuelles]
            # Die Datei "ausgang" wird im Dateisystem angelegt, aber innerhalb
            # von DoorPi mit "tueroeffner" angesprochen
            ausgang = tueroeffner
            # Die Datei "ausgang2" wird im Dateisystem angelegt, aber innerhalb
            # von DoorPi mit "fensteroeffner" angesprochen
            ausgang2 = fensteroeffner

            [keyboard_settings_rfid]
            # Der Port, mit dem der Reader verbunden ist, muss immer mit
            # angegeben werden.
            port = /dev/ttyAMA0

            [keyboard_input_rfid]
            1234567 = out:tueroeffner,1,0,3
            2345678 = out:fensteroeffner,1,0,3

            # Eine Sektion [keyboard_output_rfid] hat keinen Sinn, da ein
            # RFID-Reader nichts ausgeben kann.

        Ergebnis des Beispiels ist, dass:

        1. zwei Keyboards innerhalb von DoorPi registiert werden - das eine
           dateibasierend mit dem Namen "virtuelles", das andere ein RFID-Reader
           mit dem Namen "rfid"
        2. dem virtuellen Keyboard alle nötigen Parameter mitgegeben werden,
           beim rfid Keyboard nur die Default-Parameter genutzt werden.
        3. ein InputPin für das virtuelle Keyboard angelegt wird
        4. wenn die Datei ``!BASEPATH!/keyboards/virtuelles/inputpins/klingel``
           eine 1 als Inhalt bekommt, wird

           - Ausgang tueroeffner (in dem Fall die Datei
             ``!BASEPATH!/keyboards/virtuelles/outputpins/ausgang``)
           - neu geschrieben und bekommt den Inhalt "1"
           - es wird drei Sekunden gewartet
           - und die Datei wird neu geschrieben, diesmal mit dem Inhalt "0"
        5. ähnliches für das rfid Keyboard definiert wurde:

           - der RFID-Chip mit dem Code "1234567" öffnet den tueroeffner
           - der RFID-Chip mit dem Code "2345678" öffnet den fensteroeffner

        Wobei ``!BASEPATH!`` für das Home-Verzeichnis von DoorPi steht.
        """),
}

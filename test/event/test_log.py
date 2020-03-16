import json
import sqlite3
from ..mocks import DoorPi, DoorPiTestCase

from doorpi.event.log import EventLog


class TestEventLog(DoorPiTestCase):

    def test_creation(self):
        el = EventLog("./events.db")
        db = sqlite3.connect("events.db")
        self.assertEqual(
            "1", db.execute("SELECT value FROM metadata WHERE key = 'db_version'").fetchone()[0])
        db.close()
        el.destroy()

    def test_count(self):
        el = EventLog("./events.db")
        db = sqlite3.connect("events.db")

        with db:
            for eid in range(200):
                db.execute("INSERT INTO event_log VALUES (?, ?, ?, ?, ?)",
                           (eid, "test", "OnTest", 0, ""))
        self.assertEqual(el.count_event_log_entries(), 200)

    def test_get(self):
        el = EventLog("./events.db")
        db = sqlite3.connect("events.db")

        with db:
            for eid in range(200):
                db.execute("INSERT INTO event_log VALUES (?, ?, ?, ?, ?)",
                           (eid, "test", f"OnTimeSecond", eid * 2,
                            '{"more": "\'\\";", "things": true}'))

        log = el.get_event_log(100)
        self.assertEqual(type(log), tuple)
        self.assertEqual(len(log), 100)
        self.assertEqual(log, tuple({
            "event_id": str(eid),
            "fired_by": "test",
            "event_name": "OnTimeSecond",
            "start_time": float(eid * 2),
            "additional_infos": '{"more": "\'\\";", "things": true}'
        } for eid in range(100)))

    def test_get_filter(self):
        el = EventLog("./events.db")
        db = sqlite3.connect("events.db")

        with db:
            for eid in range(200):
                for e in ["Minute", "Hour"]:
                    db.execute("INSERT INTO event_log VALUES (?, ?, ?, ?, ?)",
                               (eid, "test", f"OnTime{e}", eid * 2,
                                '{"more": "\'\\";", "things": true}'))

        log = el.get_event_log(100, "meH")
        self.assertEqual(log, tuple({
            "event_id": str(i),
            "fired_by": "test",
            "event_name": "OnTimeHour",
            "start_time": float(i * 2),
            "additional_infos": '{"more": "\'\\";", "things": true}'
        } for i in range(100)))

    def test_log_event(self):
        el = EventLog("./events.db")
        d = {"things": True, "more": '\'\\";'}
        el.log_event("00TEST", "test", "OnTest", 0, d)
        self.assertEqual(el.get_event_log(), ({
            "event_id": "00TEST",
            "fired_by": "test",
            "event_name": "OnTest",
            "start_time": 0.0,
            "additional_infos": json.dumps(d, sort_keys=True),
        },))

    def test_log_action(self):
        el = EventLog("./events.db")
        el.log_action("00TEST", "-", 0.0)
        el.destroy()
        db = sqlite3.connect("events.db")
        cur = db.execute("SELECT * FROM action_log")
        self.assertEqual((("00TEST", "-", 0.0),), tuple((r[0], r[1], r[2]) for r in cur))

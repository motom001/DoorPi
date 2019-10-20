import json
import logging
import os
import sqlite3


logger = logging.getLogger(__name__)


class EventLog:

    def __init__(self, db):
        if not sqlite3.threadsafety:
            raise RuntimeError("Your version of SQLite is not compiled thread-safe!")

        os.makedirs(os.path.dirname(db), exist_ok=True)
        self._db = sqlite3.connect(
            database=db,
            timeout=1,
            isolation_level=None,
            check_same_thread=False
        )

        with self._db:
            self._db.executescript("""
                CREATE TABLE IF NOT EXISTS event_log (
                    event_id TEXT,
                    fired_by TEXT,
                    event_name TEXT,
                    start_time REAL,
                    additional_infos TEXT
                );
                CREATE TABLE IF NOT EXISTS action_log (
                    event_id TEXT,
                    action_name TEXT,
                    start_time REAL,
                    action_result TEXT
                );
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY ON CONFLICT REPLACE,
                    value TEXT
                );
                INSERT INTO metadata VALUES ('db_version', '1');
                """)

    def count_event_log_entries(self, filter=""):
        try:
            return self._db.execute("""
                SELECT COUNT(*) FROM event_log
                WHERE event_id LIKE ?
                OR fired_by LIKE ?
                OR event_name LIKE ?
                OR start_time LIKE ?
            """, (f"%{filter}%",) * 4).fetchone()[0]
        except Exception:
            logger.exception("Error counting event log entries with filter %s", repr(filter))
            return -1

    def get_event_log(self, max_count=100, filter=""):
        return_object = ()
        try:
            cursor = self._db.execute("""
                SELECT event_id, fired_by, event_name, start_time, additional_infos FROM event_log
                WHERE event_id LIKE ?
                OR fired_by LIKE ?
                OR event_name LIKE ?
                OR start_time LIKE ?
                ORDER BY start_time ASC
                LIMIT ?""", (f"%{filter}%",) * 4 + (max_count,))

            return_object = tuple({
                "event_id": row[0],
                "fired_by": row[1],
                "event_name": row[2],
                "start_time": row[3],
                "additional_infos": row[4]
            } for row in cursor)
        except Exception:
            logger.exception("Unable to read event log with filter %s", filter)
        return return_object

    def log_event(self, event_id, source, event, start_time, extra):
        extra = json.dumps(extra, sort_keys=True) if extra is not None else ""
        try:
            with self._db:
                self._db.execute("INSERT INTO event_log VALUES (?, ?, ?, ?, ?)",
                                 (event_id, source, event, start_time, extra))
        except Exception:
            logger.exception("[%s] Cannot insert event %s into event log", event_id, event)

    def log_action(self, event_id, action_name, start_time):
        try:
            with self._db:
                self._db.execute("INSERT INTO action_log VALUES (?, ?, ?, ?)",
                                 (event_id, action_name, start_time, ""))
        except Exception:
            logger.exception("[%s] Cannot insert action %s into event log", event_id, action)

    def destroy(self):
        self._db.close()

    __del__ = destroy

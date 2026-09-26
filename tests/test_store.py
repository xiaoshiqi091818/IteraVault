import tempfile
import unittest
from pathlib import Path

from iteravault.store import append_event, initialize, list_events


class TaskEventStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "events.sqlite3"
        initialize(self.db)

    def test_round_trip_and_task_isolation(self):
        first = append_event(self.db, "task-a", "task_started", {"goal": "写科普文章"})
        append_event(self.db, "task-b", "task_started", {"goal": "改代码"})
        append_event(self.db, "task-a", "feedback_recorded", {"comment": "缩短开头"})
        actual = list_events(self.db, "task-a")
        self.assertEqual([event.kind for event in actual], ["task_started", "feedback_recorded"])
        self.assertEqual(actual[0].id, first.id)
        self.assertEqual(actual[0].payload, {"goal": "写科普文章"})
        self.assertEqual(len(list_events(self.db, "task-b")), 1)

    def test_invalid_event_does_not_write(self):
        with self.assertRaises(ValueError):
            append_event(self.db, "task-a", "unsupported", {})
        with self.assertRaises(TypeError):
            append_event(self.db, "task-a", "task_started", [])
        self.assertEqual(list_events(self.db, "task-a"), [])

    def test_reinitialize_preserves_history(self):
        append_event(self.db, "task-a", "task_started", {"goal": "demo"})
        initialize(self.db)
        self.assertEqual(len(list_events(self.db, "task-a")), 1)


if __name__ == "__main__":
    unittest.main()

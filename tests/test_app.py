import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

import main
from app.cab import Cab
from app.ride_request import RideRequest


class TestCabMatcher(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.old_cabs = main.CABS_FILE
        self.old_save = main.SAVE_FILE
        main.CABS_FILE = os.path.join(self.folder.name, "cabs.json")
        main.SAVE_FILE = os.path.join(self.folder.name, "state.json")
        with open(main.CABS_FILE, "w") as f:
            json.dump([
                {"driver": "A", "seats": 2, "destination": "Delhi", "time_slot": "Morning"},
                {"driver": "B", "seats": 1, "destination": "Delhi", "time_slot": "Morning"},
                {"driver": "C", "seats": 4, "destination": "Jaipur", "time_slot": "Night"}
            ], f)
        self.cabs, self.queues, self.order = main.load_data()

    def tearDown(self):
        main.CABS_FILE = self.old_cabs
        main.SAVE_FILE = self.old_save
        self.folder.cleanup()

    def add(self, name, year, city="Delhi", time="Morning"):
        student = RideRequest(name, city, time, year, self.order)
        main.add_to_queue(self.queues, student)
        self.order += 1

    def test_bad_request_and_cab(self):
        for city, time, year in [("Mumbai", "Morning", 2), ("Delhi", "Noon", 2), ("Delhi", "Morning", 7)]:
            with self.assertRaises(ValueError):
                RideRequest("Test", city, time, year, 1)
        with self.assertRaises(ValueError):
            Cab("Driver", 5, "Delhi", "Morning")

    def test_seniors_first_and_same_year_order(self):
        self.add("Junior", 1)
        self.add("First third year", 3)
        self.add("Second third year", 3)
        self.add("Senior", 5)
        main.dispatch(self.cabs, self.queues, ("Delhi", "Morning"))
        self.assertEqual([s.name for s in self.cabs[0].students], ["Senior", "First third year"])
        main.dispatch(self.cabs, self.queues, ("Delhi", "Morning"))
        self.assertEqual([s.name for s in self.cabs[1].students], ["Second third year"])
        self.assertEqual([x[2].name for x in self.queues[("Delhi", "Morning")]], ["Junior"])

    def test_preview_does_not_assign_or_duplicate(self):
        self.add("First", 5)
        self.add("Second", 4)
        self.add("Third", 3)
        output = io.StringIO()
        with redirect_stdout(output):
            main.find_matches(self.cabs, self.queues)
        text = output.getvalue()
        self.assertIn("A (Delhi, Morning): First, Second", text)
        self.assertIn("B (Delhi, Morning): Third", text)
        self.assertEqual(len(self.queues[("Delhi", "Morning")]), 3)
        self.assertFalse(self.cabs[0].left)
        self.assertEqual(self.cabs[0].students, [])

    def test_half_empty_cab_cannot_leave_twice(self):
        self.add("Only one", 1)
        self.assertTrue(main.dispatch(self.cabs, self.queues, ("Delhi", "Morning")))
        self.assertTrue(self.cabs[0].left)
        self.assertEqual(len(self.cabs[0].students), 1)
        self.add("Late", 5)
        self.assertTrue(main.dispatch(self.cabs, self.queues, ("Delhi", "Morning")))
        self.assertEqual(self.cabs[1].students[0].name, "Late")

    def test_no_waiting_or_no_cab(self):
        self.assertFalse(main.dispatch(self.cabs, self.queues, ("Jaipur", "Night")))
        self.assertFalse(self.cabs[2].left)
        self.add("No ride", 5, "Jaipur", "Morning")
        self.assertFalse(main.dispatch(self.cabs, self.queues, ("Jaipur", "Morning")))
        self.assertEqual(len(self.queues[("Jaipur", "Morning")]), 1)

    def test_save_and_reload_keeps_order_and_cab_status(self):
        self.add("Earlier", 3)
        self.add("Already left", 5)
        main.dispatch(self.cabs, self.queues, ("Delhi", "Morning"))
        self.add("Still waiting", 3)
        self.add("Waiting without cab", 2, "Jaipur", "Morning")
        main.save_data(self.cabs, self.queues, self.order)
        with redirect_stdout(io.StringIO()):
            new_cabs, new_queues, new_order = main.load_data()
        self.assertEqual(new_order, self.order)
        self.assertTrue(new_cabs[0].left)
        self.assertEqual([s.name for s in new_cabs[0].students], ["Already left", "Earlier"])
        self.assertEqual([x[2].name for x in sorted(new_queues[("Delhi", "Morning")])], ["Still waiting"])
        self.assertEqual(len(new_queues[("Jaipur", "Morning")]), 1)
        newer = RideRequest("After restart", "Delhi", "Morning", 3, new_order)
        main.add_to_queue(new_queues, newer)
        main.dispatch(new_cabs, new_queues, ("Delhi", "Morning"))
        self.assertEqual(new_cabs[1].students[0].name, "Still waiting")

    def test_broken_save_starts_fresh(self):
        with open(main.SAVE_FILE, "w") as f:
            f.write("not valid json")
        with redirect_stdout(io.StringIO()):
            cabs, queues, number = main.load_data()
        self.assertEqual(number, 1)
        self.assertEqual(len(cabs), 3)
        self.assertFalse(any(queues.values()))


if __name__ == "__main__":
    unittest.main()

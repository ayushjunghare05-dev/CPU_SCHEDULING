"""Small regression test suite; run with: python -m unittest -v"""
import unittest
from scheduler import _normalise_processes, fcfs, sjf_non_preemptive, round_robin


class SchedulingTests(unittest.TestCase):
    def setUp(self):
        self.processes = _normalise_processes([
            {"pid": "P1", "arrival_time": 0, "burst_time": 5},
            {"pid": "P2", "arrival_time": 1, "burst_time": 3},
            {"pid": "P3", "arrival_time": 2, "burst_time": 8},
            {"pid": "P4", "arrival_time": 3, "burst_time": 6},
        ])

    def test_fcfs_metrics(self):
        result = fcfs(self.processes)
        by_pid = {p["pid"]: p for p in result["processes"]}
        self.assertEqual([s["pid"] for s in result["timeline"]], ["P1", "P2", "P3", "P4"])
        self.assertEqual(by_pid["P1"]["completion_time"], 5)
        self.assertEqual(by_pid["P2"]["waiting_time"], 4)
        self.assertEqual(result["metrics"]["average_waiting_time"], 5.75)

    def test_sjf_non_preemptive_order(self):
        result = sjf_non_preemptive(self.processes)
        self.assertEqual([s["pid"] for s in result["timeline"]], ["P1", "P2", "P4", "P3"])
        self.assertEqual(result["metrics"]["average_waiting_time"], 5.25)

    def test_round_robin_respects_quantum(self):
        result = round_robin(self.processes, 2)
        non_idle = [s["pid"] for s in result["timeline"]]
        self.assertEqual(non_idle[:3], ["P1", "P2", "P3"])
        self.assertTrue(all(s["duration"] <= 2 for s in result["timeline"]))
        self.assertEqual(len(result["processes"]), 4)
        self.assertEqual(sorted(p["completion_time"] for p in result["processes"]), [11, 14, 20, 22])

    def test_idle_time_is_reported(self):
        processes = _normalise_processes([{"pid": "P1", "arrival_time": 4, "burst_time": 2}])
        result = fcfs(processes)
        self.assertEqual(result["timeline"][0]["pid"], "IDLE")
        self.assertEqual(result["timeline"][0]["duration"], 4)
        self.assertEqual(result["metrics"]["cpu_utilization"], 33.33)

    def test_invalid_quantum(self):
        with self.assertRaises(ValueError):
            round_robin(self.processes, 0)

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            _normalise_processes([
                {"pid": "P1", "arrival_time": 0, "burst_time": 1},
                {"pid": "P1", "arrival_time": 1, "burst_time": 2},
            ])


if __name__ == "__main__":
    unittest.main()

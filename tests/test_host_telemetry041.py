"""Bounded local tests for CPU/memory telemetry; no sponsor calls."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from host_telemetry041 import Sampler, parse_top


class TelemetryTests(unittest.TestCase):
    def test_mac_top_parser(self):
        text = ("CPU usage: 27.10% user, 38.39% sys, 34.49% idle\n"
                "PhysMem: 15G used (3524M wired, 6329M compressor), 291M unused.\n")
        result = parse_top(text)
        self.assertEqual(result["cpu_utilization_pct"], 65.51)
        self.assertEqual(result["memory_used_bytes_approx"], 15 * 1024**3)

    def test_missing_metrics_fail_closed(self):
        with self.assertRaises(ValueError):
            parse_top("CPU load unrelated text\nMem invalid")

    def test_cpu_bounds(self):
        result = parse_top("CPU usage: 0% user, 0% sys, 150% idle\nPhysMem: 512M used")
        self.assertEqual(result["cpu_utilization_pct"], 0)

    def test_unknown_before_first_sample(self):
        value = Sampler().latest()
        self.assertEqual(value["state"], "NOT_TESTED")
        self.assertIsNone(value["sample_age_ms"])

    def test_sampler_rejected_output(self):
        with patch("host_telemetry041.platform.system", return_value="Darwin"), \
             patch("host_telemetry041.subprocess.run") as run:
            run.return_value.stdout = "bad output"
            result = Sampler().collect_once()
            self.assertEqual(result["state"], "FAILED")
            self.assertEqual(result["reason"], "ValueError")


if __name__ == "__main__":
    unittest.main()

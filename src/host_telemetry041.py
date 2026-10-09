"""Read-only macOS telemetry; sampled outside the HTTP request thread.

CPU core count and installed RAM are static inventory. Dynamic CPU utilization
and physical memory usage come from the host's top(1), not the GPU schematic.
No model, sponsor API, remote deployment, or repair action is invoked.
"""
import platform
import re
import subprocess
import threading
import time

_CPU = re.compile(r"CPU usage:\s*([\d.]+)% user,\s*([\d.]+)% sys,\s*([\d.]+)% idle")
_MEM = re.compile(r"PhysMem:\s*([\d.]+)([KMGT]) used")
_SCALE = {"K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}


def parse_top(text):
    cpu = _CPU.search(text)
    mem = _MEM.search(text)
    if not cpu or not mem:
        raise ValueError("expected CPU usage and PhysMem in macOS top output")
    util = max(0.0, min(100.0, 100.0 - float(cpu.group(3))))
    used = round(float(mem.group(1)) * _SCALE[mem.group(2)])
    return {"cpu_utilization_pct": round(util, 2),
            "memory_used_bytes_approx": used,
            "cpu_metric": "macOS top idle fraction",
            "memory_metric": "macOS top rounded PhysMem used (approximate)"}


class Sampler:
    def __init__(self, interval_s=3):
        self.interval_s = interval_s
        self._lock = threading.Lock()
        self._value = {"state": "NOT_TESTED", "source": "macOS top"}
        self._running = False

    def collect_once(self):
        if platform.system() != "Darwin":
            result = {"state": "NOT_TESTED", "reason": "macOS-only sampler"}
        else:
            try:
                out = subprocess.run(["top", "-l", "1", "-n", "0"],
                                     capture_output=True, text=True,
                                     timeout=4, check=True).stdout
                result = {"state": "OBSERVED", "source": "host OS: top -l 1 -n 0",
                          "sampled_epoch_ms": int(time.time() * 1000),
                          **parse_top(out)}
            except (OSError, subprocess.SubprocessError, ValueError) as exc:
                result = {"state": "FAILED", "source": "host OS: top",
                          "reason": type(exc).__name__}
        with self._lock:
            self._value = result.copy()
        return result

    def latest(self):
        with self._lock:
            result = self._value.copy()
        ts = result.get("sampled_epoch_ms")
        result["sample_age_ms"] = max(0, int(time.time() * 1000) - ts) if ts else None
        result["fresh"] = ts is not None and result["sample_age_ms"] < 3 * self.interval_s * 1000
        return result

    def start(self):
        if self._running:
            return
        self._running = True

        def worker():
            while self._running:
                self.collect_once()
                time.sleep(self.interval_s)
        threading.Thread(target=worker, name="read-only-host-telemetry", daemon=True).start()

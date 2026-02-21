from __future__ import annotations

import csv
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

from .config import DIRECTIONS, LoggingConfig


@dataclass
class MetricsLogger:
    config: LoggingConfig
    baseline_wait_s: float = 35.0
    start_ts: float = field(default_factory=time.time)

    def __post_init__(self):
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path = self.config.output_dir / self.config.csv_name
        self._ensure_header()

    def _ensure_header(self):
        if Path(self.csv_path).exists():
            return
        with open(self.csv_path, "w", newline="", encoding="utf-8") as fp:
            writer = csv.writer(fp)
            writer.writerow([
                "timestamp",
                *[f"count_{d}" for d in DIRECTIONS],
                *[f"density_{d}" for d in DIRECTIONS],
                "active_direction",
                "phase",
                "eta_wait_s",
                "wait_reduction_s",
            ])

    def estimate_wait(self, queue_length: Dict[str, float], active_direction: str) -> float:
        avg_queue = sum(queue_length.values()) / len(DIRECTIONS)
        advantage = queue_length.get(active_direction, 0.0)
        eta = max(6.0, avg_queue * 3.0 - advantage)
        return eta

    def log(
        self,
        counts: Dict[str, int],
        density: Dict[str, float],
        active_direction: str,
        phase: str,
        eta_wait_s: float,
    ):
        reduction = self.baseline_wait_s - eta_wait_s
        with open(self.csv_path, "a", newline="", encoding="utf-8") as fp:
            writer = csv.writer(fp)
            writer.writerow([
                time.time() - self.start_ts,
                *[counts[d] for d in DIRECTIONS],
                *[round(density[d], 4) for d in DIRECTIONS],
                active_direction,
                phase,
                round(eta_wait_s, 2),
                round(reduction, 2),
            ])

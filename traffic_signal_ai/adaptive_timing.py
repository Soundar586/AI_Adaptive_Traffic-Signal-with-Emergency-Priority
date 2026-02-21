from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from .config import DIRECTIONS, TimingConfig


@dataclass
class AdaptiveTimingEngine:
    config: TimingConfig
    previous_green: Dict[str, float] = field(default_factory=lambda: {d: 10.0 for d in DIRECTIONS})

    def compute(self, density: Dict[str, float]) -> Dict[str, float]:
        intergreen = len(DIRECTIONS) * (self.config.yellow_s + self.config.all_red_s)
        base_green = len(DIRECTIONS) * self.config.min_green_s
        available_cycle = max(self.config.cycle_floor_s, base_green + intergreen + 12.0)
        total_green_budget = max(base_green, available_cycle - intergreen)
        distributable = max(0.0, total_green_budget - base_green)

        raw = {
            d: self.config.min_green_s + density[d] * distributable
            for d in DIRECTIONS
        }
        bounded = {d: min(self.config.max_green_s, max(self.config.min_green_s, raw[d])) for d in DIRECTIONS}

        alpha = self.config.smoothing_alpha
        smoothed = {
            d: (alpha * bounded[d]) + ((1 - alpha) * self.previous_green[d])
            for d in DIRECTIONS
        }
        self.previous_green.update(smoothed)
        return smoothed

    def emergency_green(self, direction: str) -> Dict[str, float]:
        plan = {d: self.config.min_green_s for d in DIRECTIONS}
        plan[direction] = self.config.max_green_s
        self.previous_green.update(plan)
        return plan

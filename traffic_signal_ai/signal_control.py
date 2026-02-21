from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .config import DIRECTIONS, TimingConfig


@dataclass
class SignalSnapshot:
    active_direction: str
    phase: str
    time_remaining: float


class StableSignalController:
    def __init__(self, config: TimingConfig):
        self.config = config
        self.order = list(DIRECTIONS)
        self.index = 0
        self.phase = "green"
        self.timer = config.min_green_s
        self.active_direction = self.order[self.index]

    def force_emergency(self, direction: str):
        self.active_direction = direction
        self.phase = "green"
        self.timer = self.config.max_green_s
        self.index = self.order.index(direction)

    def tick(self, dt: float, plan: Dict[str, float]) -> SignalSnapshot:
        self.timer -= dt
        if self.timer <= 0:
            if self.phase == "green":
                self.phase = "yellow"
                self.timer = self.config.yellow_s
            elif self.phase == "yellow":
                self.phase = "all_red"
                self.timer = self.config.all_red_s
            else:
                self.phase = "green"
                self.index = (self.index + 1) % len(self.order)
                self.active_direction = self.order[self.index]
                self.timer = plan[self.active_direction]

        return SignalSnapshot(
            active_direction=self.active_direction,
            phase=self.phase,
            time_remaining=max(self.timer, 0.0),
        )

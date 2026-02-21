from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict

from .config import DIRECTIONS


@dataclass
class TrafficState:
    density: Dict[str, float]
    queue_length: Dict[str, float]
    emergency_direction: str | None


@dataclass
class StateEstimator:
    history_size: int = 10
    density_history: Dict[str, Deque[int]] = field(
        default_factory=lambda: {d: deque(maxlen=10) for d in DIRECTIONS}
    )

    def update(self, counts: Dict[str, int], emergency_direction: str | None) -> TrafficState:
        for direction, value in counts.items():
            self.density_history[direction].append(value)

        smoothed = {
            direction: (sum(hist) / len(hist) if hist else 0.0)
            for direction, hist in self.density_history.items()
        }
        total = sum(smoothed.values()) or 1.0
        density = {d: smoothed[d] / total for d in DIRECTIONS}
        queue = {d: smoothed[d] for d in DIRECTIONS}
        return TrafficState(density=density, queue_length=queue, emergency_direction=emergency_direction)

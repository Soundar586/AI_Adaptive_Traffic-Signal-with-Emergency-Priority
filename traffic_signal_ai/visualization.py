from __future__ import annotations

from typing import Dict, List, Tuple

import cv2
import numpy as np

from .config import DIRECTIONS, SystemConfig


class IntersectionUI:
    def __init__(self, config: SystemConfig):
        self.config = config

    def render(
        self,
        frame: np.ndarray,
        counts: Dict[str, int],
        density: Dict[str, float],
        active_direction: str,
        phase: str,
        timer: float,
        boxes: Dict[str, List[Tuple[int, int, int, int]]],
        wait_eta: float,
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        panel = frame.copy()
        for direction in DIRECTIONS:
            x1f, y1f, x2f, y2f = self.config.roi_map[direction]
            x1, y1, x2, y2 = int(x1f * w), int(y1f * h), int(x2f * w), int(y2f * h)
            color = (0, 255, 0) if direction == active_direction and phase == "green" else (50, 50, 255)
            cv2.rectangle(panel, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                panel,
                f"{direction[:1].upper()} cnt:{counts[direction]} dens:{density[direction]:.2f}",
                (x1 + 5, y1 + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
                cv2.LINE_AA,
            )
            for bx, by, bw, bh in boxes[direction]:
                cv2.rectangle(panel, (bx, by), (bx + bw, by + bh), (255, 180, 0), 1)

        cv2.putText(panel, f"PHASE: {phase.upper()} | GREEN: {active_direction.upper()} | T-{timer:.1f}s", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(panel, f"Estimated avg wait: {wait_eta:.1f}s", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(panel, "Press q to quit", (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 1)
        return panel

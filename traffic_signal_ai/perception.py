from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import cv2
import numpy as np

from .config import DIRECTIONS, SystemConfig


@dataclass
class DetectionResult:
    counts: Dict[str, int]
    emergency_direction: str | None
    boxes: Dict[str, List[Tuple[int, int, int, int]]]


class TrafficPerception:
    """Perception stage using motion-based vehicle proxy detection."""

    def __init__(self, config: SystemConfig):
        self.config = config
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=25)
        self.prev_roi_brightness = {d: 1.0 for d in DIRECTIONS}

    def _roi_pixels(self, frame: np.ndarray, direction: str) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
        h, w = frame.shape[:2]
        x1f, y1f, x2f, y2f = self.config.roi_map[direction]
        x1, y1, x2, y2 = int(x1f * w), int(y1f * h), int(x2f * w), int(y2f * h)
        return frame[y1:y2, x1:x2], (x1, y1, x2, y2)

    def process(self, frame: np.ndarray) -> DetectionResult:
        mask = self.bg_subtractor.apply(frame)
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        counts: Dict[str, int] = {d: 0 for d in DIRECTIONS}
        boxes: Dict[str, List[Tuple[int, int, int, int]]] = {d: [] for d in DIRECTIONS}
        emergency_direction = None

        for direction in DIRECTIONS:
            roi, (x1, y1, x2, y2) = self._roi_pixels(frame, direction)
            roi_mask = mask[y1:y2, x1:x2]
            contours, _ = cv2.findContours(roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if cv2.contourArea(contour) < self.config.detection.min_contour_area:
                    continue
                x, y, w, h = cv2.boundingRect(contour)
                counts[direction] += 1
                boxes[direction].append((x + x1, y + y1, w, h))

            brightness = float(np.mean(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY))) + 1e-6
            ratio = brightness / self.prev_roi_brightness[direction]
            self.prev_roi_brightness[direction] = brightness
            if ratio > self.config.detection.emergency_flash_ratio and counts[direction] > 0:
                emergency_direction = direction

        return DetectionResult(counts=counts, emergency_direction=emergency_direction, boxes=boxes)

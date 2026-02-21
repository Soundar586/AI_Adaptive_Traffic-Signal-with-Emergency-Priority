from __future__ import annotations

import time
from dataclasses import dataclass

import cv2

from .adaptive_timing import AdaptiveTimingEngine
from .config import SystemConfig
from .metrics import MetricsLogger
from .perception import TrafficPerception
from .signal_control import StableSignalController
from .state_estimation import StateEstimator
from .visualization import IntersectionUI


@dataclass
class IntersectionController:
    config: SystemConfig

    def __post_init__(self):
        self.perception = TrafficPerception(self.config)
        self.estimator = StateEstimator()
        self.timing = AdaptiveTimingEngine(self.config.timing)
        self.signal = StableSignalController(self.config.timing)
        self.metrics = MetricsLogger(self.config.logging)
        self.ui = IntersectionUI(self.config)

    def run(self, source: str | int = 0):
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise RuntimeError(f"Unable to open source {source}")

        last = time.time()
        plan = {d: self.config.timing.min_green_s for d in self.config.roi_map}

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.resize(frame, (self.config.frame_width, self.config.frame_height))

            detection = self.perception.process(frame)
            state = self.estimator.update(detection.counts, detection.emergency_direction)

            if state.emergency_direction:
                plan = self.timing.emergency_green(state.emergency_direction)
                self.signal.force_emergency(state.emergency_direction)
            else:
                plan = self.timing.compute(state.density)

            now = time.time()
            dt = now - last
            last = now
            snapshot = self.signal.tick(dt, plan)

            wait_eta = self.metrics.estimate_wait(state.queue_length, snapshot.active_direction)
            self.metrics.log(
                counts=detection.counts,
                density=state.density,
                active_direction=snapshot.active_direction,
                phase=snapshot.phase,
                eta_wait_s=wait_eta,
            )

            overlay = self.ui.render(
                frame=frame,
                counts=detection.counts,
                density=state.density,
                active_direction=snapshot.active_direction,
                phase=snapshot.phase,
                timer=snapshot.time_remaining,
                boxes=detection.boxes,
                wait_eta=wait_eta,
            )
            cv2.imshow("AI Adaptive Traffic Signal", overlay)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

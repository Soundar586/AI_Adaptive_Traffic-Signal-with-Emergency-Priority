from traffic_signal_ai.adaptive_timing import AdaptiveTimingEngine
from traffic_signal_ai.config import TimingConfig
from traffic_signal_ai.signal_control import StableSignalController


def test_adaptive_timing_allocates_more_to_heavy_direction():
    engine = AdaptiveTimingEngine(TimingConfig())
    density = {"north": 0.7, "south": 0.1, "east": 0.1, "west": 0.1}
    plan = engine.compute(density)
    assert plan["north"] > plan["south"]
    assert plan["north"] > plan["east"]


def test_emergency_forces_priority_green():
    cfg = TimingConfig(max_green_s=40.0)
    controller = StableSignalController(cfg)
    controller.force_emergency("west")
    snap = controller.tick(0.1, {"north": 8.0, "south": 8.0, "east": 8.0, "west": 8.0})
    assert snap.active_direction == "west"
    assert snap.phase == "green"

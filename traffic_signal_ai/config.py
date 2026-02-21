from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple

DIRECTIONS = ("north", "south", "east", "west")


@dataclass
class TimingConfig:
    min_green_s: float = 8.0
    max_green_s: float = 35.0
    yellow_s: float = 3.0
    all_red_s: float = 1.0
    cycle_floor_s: float = 45.0
    smoothing_alpha: float = 0.35


@dataclass
class DetectionConfig:
    min_contour_area: int = 800
    emergency_flash_ratio: float = 1.45
    vehicle_departure_rate: float = 1.8


@dataclass
class LoggingConfig:
    output_dir: Path = Path("logs")
    csv_name: str = "traffic_metrics.csv"


@dataclass
class SystemConfig:
    frame_width: int = 1280
    frame_height: int = 720
    roi_map: Dict[str, Tuple[float, float, float, float]] = field(
        default_factory=lambda: {
            "north": (0.35, 0.00, 0.65, 0.40),
            "south": (0.35, 0.60, 0.65, 1.00),
            "east": (0.60, 0.35, 1.00, 0.65),
            "west": (0.00, 0.35, 0.40, 0.65),
        }
    )
    timing: TimingConfig = field(default_factory=TimingConfig)
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

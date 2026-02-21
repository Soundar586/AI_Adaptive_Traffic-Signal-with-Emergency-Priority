import argparse

from traffic_signal_ai import SystemConfig
from traffic_signal_ai.controller import IntersectionController


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI adaptive traffic signal with emergency preemption")
    parser.add_argument("--source", default="0", help="Camera index (e.g., 0) or video file path")
    return parser.parse_args()


def main():
    args = parse_args()
    source = int(args.source) if str(args.source).isdigit() else args.source
    controller = IntersectionController(SystemConfig())
    controller.run(source=source)


if __name__ == "__main__":
    main()

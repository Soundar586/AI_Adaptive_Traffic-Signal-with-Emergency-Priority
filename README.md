# AI Adaptive Traffic Signal with Emergency Priority

This project implements a **modular, real-time traffic signal control pipeline** for a four-way intersection:

1. **Perception**: Vehicle proxy detection from camera/video frames using motion segmentation.
2. **State estimation**: Direction-wise congestion (North/South/East/West) and queue estimation.
3. **Adaptive timing**: Green times allocated in proportion to density with min/max bounds and smoothing.
4. **Signal control**: Stable finite-state phase control (`green -> yellow -> all_red`) with timers.
5. **Emergency override**: Flash-pattern heuristic preemption that forces immediate green to the emergency direction.
6. **UI + Logging**: On-frame visualization of counts, densities, active phase/timer, and CSV metric logging.

## Features

- Real-time operation from webcam (`--source 0`) or recorded video path
- Directional traffic density estimation for N/S/E/W
- Adaptive green timing to reduce average waiting time relative to fixed-cycle baseline
- Emergency vehicle priority preemption
- Real-time dashboard over video feed
- CSV logging of counts, density, active phase, estimated wait, and wait reduction
- Modular architecture suitable for iterative upgrades and hardware deployment

## Project structure

- `traffic_signal_ai/perception.py` – real-time vehicle/motion detection and emergency cues
- `traffic_signal_ai/state_estimation.py` – queue and normalized density estimator
- `traffic_signal_ai/adaptive_timing.py` – congestion-proportional green scheduler
- `traffic_signal_ai/signal_control.py` – robust signal phase engine
- `traffic_signal_ai/metrics.py` – wait-time estimation + CSV logging
- `traffic_signal_ai/visualization.py` – real-time UI overlay
- `traffic_signal_ai/controller.py` – end-to-end orchestrator pipeline
- `main.py` – runnable entry point

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py --source 0
```

or run on a file:

```bash
python main.py --source data/intersection.mp4
```

Press `q` to stop.

## Metrics and performance evaluation

Logs are written to `logs/traffic_metrics.csv` with:

- per-direction counts and densities
- active signal and phase
- estimated average wait time
- estimated wait reduction from a baseline (~35s, configurable)

This supports iterative model/timing tuning toward the target waiting-time reduction objective.

## Notes for productization

- Replace motion proxy detector with a trained detector (e.g., YOLO) for accurate classes.
- Add dedicated emergency class detection (ambulance/police/fire truck) and siren audio fusion.
- Connect `StableSignalController` outputs to PLC/IoT relay APIs for field deployment.
- Introduce multi-intersection coordination via V2X and edge/cloud telemetry.

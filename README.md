# immune-cell-simulator

Agent-based computational simulation of T-cell immune responses using Mesa.

## Overview & Purpose
immune-cell-simulator models T-cell population dynamics, pathogen detection, and inflammatory response management in a 2D grid environment using agent-based modeling techniques.

## Key Features
- Agent classes for T-cells, antigens, and tissue environments.
- Real-time cell state plotting and tracking.
- Parameter configuration for mutation rates and cell death.

## Tech Stack & Dependencies
- **Language**: Python 3.9+
- **ABM Framework**: Mesa
- **Visualization**: Matplotlib, NumPy

## Project Structure
```text
immune-cell-simulator/
├── run_simulation.py
├── model.py
├── agent.py
└── README.md
```

## Installation & Setup

### Prerequisites
- Python 3.9+

### Steps
```bash
git clone https://github.com/zsomborturcsanyi7-lang/immune-cell-simulator.git
cd immune-cell-simulator
pip install mesa matplotlib numpy
python run_simulation.py
```

## Usage Examples
```bash
python run_simulation.py --steps 500 --t-cells 100
```

## Status & License
Status: In Silico Simulation.
License: MIT

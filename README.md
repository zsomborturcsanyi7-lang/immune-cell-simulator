# ADT-T Cell — Adaptive T-Cell Simulator

**Status:** ⚠️ Prototype — Mesa simulation runs, AlphaFold integration pending


**Agent-based (Mesa) simulation modeling adaptive T-cell behavior: stress monitoring, authentication, and targeted elimination. Enhanced with AlphaFold protein structure prediction.**

## ⚠️ THIS PROJECT IS UNFINISHED — FEEL FREE TO CONTINUE IT ⚠️

**Ez a projekt NINCS KÉSZEN. Bárki folytathatja, aki akarja!**
Ezt a projektet Zsombi & Hermes Agent (Nous Research) közösen fejlesztette, de egyik projekt sincs 100%-osan befejezve. Ha tetszik az ötlet és tovább fejlesztenéd, nyugodtan fork-old, folytasd, és csinálj belőle valami nagyszerűt!

---


## 🧫 Description

The ADT-T Cell project is a complex biological simulation that features:

- **T-cell behavior modeling** — adaptive immune response simulation
- **Multiple simulation modes** — basic, clinical, evolutionary, broadcast, apocalypse
- **AlphaFold integration** — protein structure prediction (CIF format)
- **Mesa agent-based model** — cells as autonomous agents
- **Visualization** — matplotlib charts and figures

### Simulation Modes

| Mode | File | Description |
|-----|------|--------|
| Basic | `adt_simulation.py` | T-cell stress sensing and elimination |
| Clinical | `clinical_simulation.py` | Clinical environment modeling |
| Evolutionary | `evolutionary_simulation.py` | Evolutionary adaptation simulation |
| Broadcast | `broadcast_simulation.py` | Signal broadcast modeling |
| High Resolution | `high_res_analysis.py` | Detailed analysis |
| Apocalypse | `apocalypse_simulation.py` | Extreme stress scenario |

## 📁 File Structure

```
ADT-T cell/
├── adt-simulator/
│   ├── scripts/
│   │   ├── adt_simulation.py       # Basic simulation (173 lines)
│   │   ├── clinical_simulation.py  # Clinical simulation
│   │   ├── evolutionary_simulation.py # Evolutionary simulation
│   │   ├── broadcast_simulation.py # Broadcast simulation
│   │   ├── high_res_analysis.py    # High-resolution analysis
│   │   └── apocalypse_simulation.py # Apocalypse simulation
│   ├── assets/
│   │   ├── apocalypse_test.png     # Apocalypse test figure
│   │   ├── clinical_rescue_test.png # Clinical rescue test
│   │   ├── evolutionary_test.png   # Evolutionary test
│   │   ├── broadcast_test.png      # Broadcast test
│   │   └── high_res_latency.png    # High-resolution latency
│   ├── docs/
│   │   ├── ADT_WHITE_PAPER.md      # Scientific white paper
│   │   └── ADT_PROJECT_MASTER_SUMMARY.md # Project summary
│   ├── fold_2026_05_23_19_17/      # AlphaFold predictions
│   │   ├── fold_*_model_*.cif      # 3D protein structures (CIF)
│   │   ├── fold_*_full_data_*.json # Full prediction data
│   │   ├── fold_*_summary_confidences_*.json # Confidence scores
│   │   ├── templates/              # Template structures
│   │   └── msas/                   # Multiple Sequence Alignments
│   ├── fold_2026_05_23_19_17 (1)/  # Second AlphaFold run
│   ├── README.md
│   └── README_OLD.md
└── README.md
```

## 🚀 Usage

### Basic T-Cell Simulation

```bash
cd adt-simulator
python scripts/adt_simulation.py
```

### Clinical Simulation

```bash
python scripts/clinical_simulation.py
```

### Evolutionary Simulation

```bash
python scripts/evolutionary_simulation.py
```

### Broadcast Signaling

```bash
python scripts/broadcast_simulation.py
```

### High-Resolution Analysis

```bash
python scripts/high_res_analysis.py
```

### Apocalypse Simulation

```bash
python scripts/apocalypse_simulation.py
```

## 📦 Dependencies

```bash
pip install mesa matplotlib numpy
```

- **Python 3.8+**
- **Mesa** — agent-based modeling framework
- **matplotlib** — visualization
- **numpy** — numerical computing

## 🧬 Simulation Model

### Agent Types

```
HostCell
├── infected: bool       # Whether the cell is infected
├── acidic: bool         # Acidic environment (false alarm)
└── stress_signal: bool  # Stress signal

ADTTCell
├── authorized_cells: set  # Authenticated targets
├── move()                 # Movement on the grid
└── step()
    ├── Movement
    ├── Stress signal detection
    ├── Authentication request (ping)
    └── Elimination (authenticated only)
```

### Operating Principle

1. **Host cells** emit stress signals (infection OR acidic environment)
2. **ADT T-cells** detect stress signals
3. The T-cell requests **authentication** (ping mechanism)
4. **Only authenticated** targets are eliminated
5. False alarms (acidic environment) are ignored

### AlphaFold Integration

The project includes **two AlphaFold prediction runs**:
- Protein structures in CIF format
- Confidence scores (pLDDT)
- Multiple sequence alignments (MSA)
- Template-based modeling

## 📊 Results

Simulations yield the following:

| Simulation | Output |
|-----------|---------|
| Basic | T-cell elimination accuracy |
| Clinical | Therapeutic rescue rates |
| Evolutionary | Adaptation time and efficiency |
| Broadcast | Signal propagation speed |
| Apocalypse | Extreme stress survival rate |

## 🔬 Scientific Background

The ADT-T cell concept models an **adaptive, authentication-based** immunotherapeutic approach where T-cells do not eliminate blindly but instead:

1. Sense stress signals
2. Authenticate targets
3. Attack only validated threats

This mechanism reduces autoimmune reactions and increases therapeutic specificity.

Detailed documentation: `docs/ADT_WHITE_PAPER.md`

## Developer

Zsombi & Hermes Agent (Nous Research)

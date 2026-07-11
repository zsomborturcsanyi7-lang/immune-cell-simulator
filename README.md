# ADT-T Cell — Adaptív T-Sejt Szimulátor

**Ágens-alapú (Mesa) szimuláció, amely az adaptív T-sejtek működését modellezi: stressz monitorozás, hitelesítés, és célzott elimináció. AlphaFold fehérjeszerkezet predikcióval kiegészítve.**

## 🧫 Leírás

Az ADT-T Cell projekt egy komplex biológiai szimuláció, amely:

- **T-sejt viselkedés modellezése** — adaptív immunválasz szimuláció
- **Több szimulációs mód** — alap, klinikai, evolúciós, broadcast, apokalipszis
- **AlphaFold integráció** — fehérjeszerkezet predikció (CIF formátum)
- **Mesa ágens-alapú modell** — sejtek, mint autonóm ágensek
- **Vizualizáció** — matplotlib grafikonok és ábrák

### Szimulációs módok

| Mód | Fájl | Leírás |
|-----|------|--------|
| Alap | `adt_simulation.py` | T-sejt stressz érzékelés és elimináció |
| Klinikai | `clinical_simulation.py` | Klinikai környezet modellezése |
| Evolúciós | `evolutionary_simulation.py` | Evolúciós adaptáció szimuláció |
| Broadcast | `broadcast_simulation.py` | Jelátviteli broadcast modellezés |
| Nagy felbontás | `high_res_analysis.py` | Részletes elemzés |
| Apokalipszis | `apocalypse_simulation.py` | Extrém stressz szcenárió |

## 📁 Fájlszerkezet

```
ADT-T cell/
├── adt-simulator/
│   ├── scripts/
│   │   ├── adt_simulation.py       # Alap szimuláció (173 sor)
│   │   ├── clinical_simulation.py  # Klinikai szimuláció
│   │   ├── evolutionary_simulation.py # Evolúciós szimuláció
│   │   ├── broadcast_simulation.py # Broadcast szimuláció
│   │   ├── high_res_analysis.py    # Nagy felbontású elemzés
│   │   └── apocalypse_simulation.py # Apokalipszis szimuláció
│   ├── assets/
│   │   ├── apocalypse_test.png     # Apokalipszis teszt ábra
│   │   ├── clinical_rescue_test.png # Klinikai mentés teszt
│   │   ├── evolutionary_test.png   # Evolúciós teszt
│   │   ├── broadcast_test.png      # Broadcast teszt
│   │   └── high_res_latency.png    # Nagy felbontású latency
│   ├── docs/
│   │   ├── ADT_WHITE_PAPER.md      # Tudományos white paper
│   │   └── ADT_PROJECT_MASTER_SUMMARY.md # Projekt összefoglaló
│   ├── fold_2026_05_23_19_17/      # AlphaFold predikciók
│   │   ├── fold_*_model_*.cif      # 3D fehérjeszerkezetek (CIF)
│   │   ├── fold_*_full_data_*.json # Teljes predikciós adatok
│   │   ├── fold_*_summary_confidences_*.json # Konfidencia értékek
│   │   ├── templates/              # Templát szerkezetek
│   │   └── msas/                   # Multiple Sequence Alignment
│   ├── fold_2026_05_23_19_17 (1)/  # Második AlphaFold futtatás
│   ├── README.md
│   └── README_OLD.md
└── README.md
```

## 🚀 Használat

### Alap T-sejt szimuláció

```bash
cd adt-simulator
python scripts/adt_simulation.py
```

### Klinikai szimuláció

```bash
python scripts/clinical_simulation.py
```

### Evolúciós szimuláció

```bash
python scripts/evolutionary_simulation.py
```

### Broadcast jelátvitel

```bash
python scripts/broadcast_simulation.py
```

### Nagy felbontású elemzés

```bash
python scripts/high_res_analysis.py
```

### Apokalipszis szimuláció

```bash
python scripts/apocalypse_simulation.py
```

## 📦 Függőségek

```bash
pip install mesa matplotlib numpy
```

- **Python 3.8+**
- **Mesa** — ágens-alapú modellezési keretrendszer
- **matplotlib** — vizualizáció
- **numpy** — numerikus számítások

## 🧬 Szimulációs modell

### Ágens típusok

```
HostCell
├── infected: bool       # Fertőzött-e a sejt
├── acidic: bool         # Savas környezet (téves riasztás)
└── stress_signal: bool  # Stressz jelzés

ADTTCell
├── authorized_cells: set  # Hitelesített célpontok
├── move()                 # Mozgás a rácson
└── step()
    ├── Mozgás
    ├── Stressz jel érzékelés
    ├── Hitelesítés kérése (ping)
    └── Elimináció (csak hitelesítve)
```

### Működési elv

1. **Host sejtek** stressz jelet bocsátanak ki (fertőzés VAGY savas környezet)
2. **ADT T-sejtek** érzékelik a stressz jeleket
3. A T-sejt **hitelesítést** kér (ping mechanism)
4. **Csak hitelesített** célpontokat eliminál
5. A téves riasztásokat (savas környezet) figyelmen kívül hagyja

### AlphaFold integráció

A projekt tartalmaz **két AlphaFold predikciós futtatást**:
- Fehérjeszerkezetek CIF formátumban
- Konfidencia értékek (pLDDT)
- Többszörös szekvencia illesztések (MSA)
- Templát alapú modellezés

## 📊 Eredmények

A szimulációk a következőket mutatják:

| Szimuláció | Kimenet |
|-----------|---------|
| Alap | T-sejt eliminációs pontosság |
| Klinikai | Terápiás rescue ráták |
| Evolúciós | Adaptációs idő és hatékonyság |
| Broadcast | Jelterjedési sebesség |
| Apokalipszis | Extrém stressz túlélési ráta |

## 🔬 Tudományos háttér

Az ADT-T sejt koncepció egy **adaptív, hitelesítés-alapú** immunterápiás megközelítést modellez, ahol a T-sejtek nem vakon eliminálnak, hanem:

1. Érzékelik a stressz jeleket
2. Hitelesítik a célpontokat
3. Csak validált veszélyforrásokat támadnak

Ez a mechanizmus csökkenti az autoimmun reakciókat és növeli a terápia specificitását.

Részletes dokumentáció: `docs/ADT_WHITE_PAPER.md`

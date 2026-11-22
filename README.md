# MEG 315: AD-HTC Integrated Biorefinery Dashboard

> **Applied Thermodynamics, Group 28, University of Lagos**
> A full-stack thermodynamic simulation dashboard for an Anaerobic Digestion and Hydrothermal Carbonization (AD-HTC) biomass power plant.

Repository: [github.com/hamzahdrill/GROUP-28_COURSE-PROJECT](https://github.com/hamzahdrill/GROUP-28_COURSE-PROJECT)

## Overview

This project was built for MEG 315, Applied Thermodynamics, at the University of Lagos. It simulates and visualises the thermodynamic behaviour of an integrated AD-HTC biorefinery using a **FastAPI backend**, a **SQLite database** and an **interactive HTML/JavaScript frontend**.

> Potrč, S., Petrovič, A., Egieya, J. M., & Čuček, L. (2025). Valorization of biomass through anaerobic digestion and hydrothermal carbonization. *Energies, 18*(2), 334.

## Features

- **FastAPI backend:** Python REST API with 4 endpoints for calculations and data
- **SQLite database:** 12 biomass feedstocks and calculation history
- **Pydantic validation:** typed input and output models for all API data
- **Biogas ICE (Otto cycle):** T-s diagram with 4 state points
- **Rankine steam cycle:** h-s Mollier diagram with pump, boiler, turbine and condenser
- **Heat integration:** CHP waste heat against AD and HTC thermal demand
- **Animated process schematic:** SVG material flow from AD to CHP to HTC to hydrochar
- **Mass and energy charts:** daily biogas, digestate, hydrochar, electricity and thermal outputs
- **12 feedstock types:** cow manure, food waste, corn stover, microalgae, wood chips and more
- **HTC temperature slider:** adjustable hydrothermal carbonization temperature (180 to 260 °C)
- **Dual mode:** works with the API backend or standalone in any browser

## Tech stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| Backend | Python, FastAPI | REST API for cycle calculations |
| Database | SQLite | Feedstock storage and calculation history |
| Validation | Pydantic | Input and output data models |
| Frontend | HTML, CSS, JavaScript | Interactive dashboard |
| Charts | Chart.js | T-s, h-s, energy, mass and heat charts |
| Styling | Tailwind CSS | Responsive layout |
| Schematic | SVG (programmatic) | Animated process flow diagram |

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/` | Serve the dashboard HTML |
| GET | `/api/feedstocks` | Return all 12 feedstocks from SQLite |
| POST | `/api/analyze` | Run the full cycle analysis and store it in the database |
| GET | `/api/history` | Return past calculation results |

Interactive API docs are at `http://localhost:8000/docs` (Swagger UI).

## Project structure

```
GROUP-28_COURSE-PROJECT/
├── main.py                  # FastAPI backend (endpoints and calculation engine)
├── database.py              # SQLite database (feedstocks and calculations tables)
├── models.py                # Pydantic input and output models
├── ad-htc-biomass-v2.html   # Interactive frontend dashboard
├── requirements.txt         # Python dependencies
└── README.md
```

## Quick start

### Option A: full stack (API and database)

```bash
git clone https://github.com/hamzahdrill/GROUP-28_COURSE-PROJECT.git
cd GROUP-28_COURSE-PROJECT
pip install -r requirements.txt
python main.py
```

Then open http://localhost:8000 (API docs at http://localhost:8000/docs).

### Option B: standalone

Open `ad-htc-biomass-v2.html` directly in a browser. All calculations run locally in JavaScript.

## Thermodynamic concepts

| Concept | Application |
| --- | --- |
| First law | CHP energy balance (electrical and thermal output) |
| Second law and exergy | Irreversibility in combustion and heat transfer |
| Otto cycle | Biogas ICE T-s diagram (4 states) |
| Rankine cycle | Steam cycle h-s Mollier diagram |
| Heat integration | CHP waste heat cascaded to AD and HTC |
| Mass balance | AD digestate, HTC hydrochar and process water flows |
| LHV and HHV | Biogas lower heating value, hydrochar higher heating value |

## Status of results

The sample-results table has been removed from this README while the calculation outputs are being re-verified (units and energy balance). Run the dashboard to see current outputs.

## Authors

**Group 28**, MEG 315 Applied Thermodynamics, Department of Mechanical Engineering, University of Lagos, February 2026.

*Built for academic purposes as part of MEG 315 coursework.*

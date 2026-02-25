# MEG 315 — AD-HTC Integrated Biorefinery Dashboard

> **Applied Thermodynamics · Group 28 · University of Lagos (UNILAG)**  
> A full-stack thermodynamic simulation dashboard for an Anaerobic Digestion – Hydrothermal Carbonization (AD-HTC) biomass power plant.

🔗 **Repository:** [github.com/hamzahdrill/GROUP-28_COURSE-PROJECT](https://github.com/hamzahdrill/GROUP-28_COURSE-PROJECT)

---

## Overview

This project was built as part of MEG 315 — Applied Thermodynamics at the University of Lagos. It simulates and visualises the thermodynamic behaviour of an integrated AD-HTC biorefinery system using a **FastAPI backend**, **SQLite database**, and **interactive HTML/JavaScript frontend**.

> Potrč, S., Petrovič, A., Egieya, J. M., & Čuček, L. (2025). Valorization of biomass through anaerobic digestion and hydrothermal carbonization. *Energies, 18*(2), 334.

---

## Features

- **FastAPI Backend** — Python REST API with 4 endpoints for calculations and data
- **SQLite Database** — 12 biomass feedstocks + calculation history storage
- **Pydantic Validation** — Typed input/output models for all API data
- **Biogas ICE (Otto Cycle)** — T-s diagram with 4 state points
- **Rankine Steam Cycle** — h-s Mollier diagram with pump, boiler, turbine, condenser
- **Heat Integration** — CHP waste heat vs. AD and HTC thermal demand
- **Animated Process Schematic** — SVG material flow: AD → CHP → HTC → Hydrochar
- **Mass & Energy Charts** — daily biogas, digestate, hydrochar, electricity, thermal outputs
- **12 Feedstock Types** — cow manure, food waste, corn stover, microalgae, wood chips, and more
- **HTC Temperature Slider** — adjustable hydrothermal carbonization (180–260°C)
- **Dual Mode** — works with API backend *or* standalone in any browser

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Python / FastAPI | RESTful API for cycle calculations |
| **Database** | SQLite | Feedstock storage + calculation history |
| **Validation** | Pydantic | Input/output data models |
| **Frontend** | HTML / CSS / JavaScript | Interactive dashboard UI |
| **Charts** | Chart.js | T-s, h-s, energy, mass, heat charts |
| **Styling** | Tailwind CSS | Responsive layout |
| **Schematic** | SVG (programmatic) | Animated process flow diagram |
| **Fonts** | Google Fonts (DM Sans / DM Mono) | Typography |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serve the dashboard HTML |
| `GET` | `/api/feedstocks` | Return all 12 feedstocks from SQLite |
| `POST` | `/api/analyze` | Run full cycle analysis + store in DB |
| `GET` | `/api/history` | Return past calculation results |

Interactive API docs available at `http://localhost:8000/docs` (Swagger UI).

---

## Project Structure

```
GROUP-28_COURSE-PROJECT/
├── main.py                  # FastAPI backend (4 endpoints + calculation engine)
├── database.py              # SQLite database (feedstocks + calculations tables)
├── models.py                # Pydantic input/output data models
├── ad-htc-biomass-v2.html   # Interactive frontend dashboard
├── requirements.txt         # Python dependencies
├── generate_slides.py       # PowerPoint presentation generator
├── generate_report.py       # Technical report (.docx) generator
├── Group28_AD-HTC_Slides_Final.pptx   # Generated presentation (16 slides)
├── Group28_AD-HTC_Report.docx         # Generated technical report
└── README.md                # This file
```

---

## Quick Start

### Option A — Full-Stack (API + Database)

```bash
# Clone the repository
git clone https://github.com/hamzahdrill/GROUP-28_COURSE-PROJECT.git
cd GROUP-28_COURSE-PROJECT

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py

# Open in browser
# http://localhost:8000
# API docs: http://localhost:8000/docs
```

### Option B — Standalone (No Installation)

Open `ad-htc-biomass-v2.html` directly in any web browser. All calculations run locally in JavaScript.

---

## Thermodynamic Concepts

| Concept | Application |
|---|---|
| First Law of Thermodynamics | CHP energy balance (electrical + thermal output) |
| Second Law / Exergy | Irreversibility in combustion and heat transfer |
| Otto Cycle | Biogas ICE T-s diagram (4 states) |
| Rankine Cycle | Steam cycle h-s Mollier diagram |
| Heat Integration | CHP waste heat → AD + HTC cascade |
| Mass Balance | AD digestate, HTC hydrochar, process water flows |
| LHV / HHV | Biogas lower heating value, hydrochar higher heating value |

---

## Sample Results (Cow Manure, 10 t/day)

| Metric | Value |
|---|---|
| Otto Cycle Efficiency | 72.6% |
| Rankine Cycle Efficiency | 27.7% |
| Electrical Power | 18,819 kW |
| Biogas Volume | 403 m³/day |
| Heat Balance | +4,556 kW (SURPLUS) |
| Hydrochar Output | 277 kg/day |

---

## Authors

**Group 28** — MEG 315 Applied Thermodynamics  
Department of Mechanical Engineering  
University of Lagos · February 2026

---

*Built for academic purposes as part of MEG 315 — Applied Thermodynamics coursework.*

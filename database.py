"""
SQLite database for the AD-HTC Biorefinery Dashboard.
Tables: feedstocks (12 biomass types) and calculations (analysis history).
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adhtc.db")


def get_connection():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables and seed feedstock data if not already present."""
    conn = get_connection()
    c = conn.cursor()

    # ── Feedstocks table ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedstocks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            key         TEXT UNIQUE NOT NULL,
            name        TEXT NOT NULL,
            ts          REAL NOT NULL,
            vs          REAL NOT NULL,
            biogas_yield REAL NOT NULL,
            ch4         REAL NOT NULL,
            htc_yield   REAL NOT NULL,
            htc_hhv     REAL NOT NULL
        )
    """)

    # ── Calculations history table ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS calculations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT NOT NULL,
            feedstock   TEXT NOT NULL,
            inputs      TEXT NOT NULL,
            otto_results TEXT NOT NULL,
            rankine_results TEXT NOT NULL,
            heat_balance REAL NOT NULL,
            biogas_vol  REAL NOT NULL,
            elec_power  REAL NOT NULL,
            hydrochar   REAL NOT NULL
        )
    """)

    # ── Seed feedstocks if empty ──
    count = c.execute("SELECT COUNT(*) FROM feedstocks").fetchone()[0]
    if count == 0:
        feedstocks = [
            ("cow_manure",    "Cow Manure",               0.18, 0.80, 0.280, 0.60, 0.48, 14500),
            ("food_waste",    "Food / Kitchen Waste",      0.25, 0.90, 0.550, 0.62, 0.45, 19800),
            ("sewage_sludge", "Sewage Sludge",             0.30, 0.70, 0.300, 0.58, 0.50, 15000),
            ("corn_stover",   "Corn Stover",               0.88, 0.85, 0.338, 0.55, 0.55, 21500),
            ("rice_husk",     "Rice Husk",                 0.90, 0.80, 0.250, 0.52, 0.58, 18200),
            ("sugarcane",     "Sugarcane Bagasse",          0.50, 0.90, 0.310, 0.54, 0.52, 20100),
            ("pig_manure",    "Pig Manure",                0.20, 0.82, 0.320, 0.62, 0.46, 15200),
            ("wood_chips",    "Wood Chips",                0.85, 0.92, 0.200, 0.55, 0.65, 24000),
            ("msw",           "Municipal Solid Waste",     0.60, 0.75, 0.400, 0.58, 0.50, 17500),
            ("algae",         "Microalgae",                0.10, 0.85, 0.450, 0.65, 0.40, 22000),
            ("cassava",       "Cassava Peel",              0.88, 0.86, 0.420, 0.58, 0.48, 19200),
            ("palm_waste",    "Palm Empty Fruit Bunch",    0.78, 0.85, 0.270, 0.53, 0.60, 20800),
        ]
        c.executemany(
            "INSERT INTO feedstocks (key, name, ts, vs, biogas_yield, ch4, htc_yield, htc_hhv) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            feedstocks,
        )

    conn.commit()
    conn.close()


def get_all_feedstocks():
    """Return all feedstocks as a list of dicts."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM feedstocks ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_feedstock_by_key(key: str):
    """Return a single feedstock by its key."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM feedstocks WHERE key = ?", (key,)).fetchone()
    conn.close()
    return dict(row) if row else None


def save_calculation(feedstock: str, inputs: dict, otto: dict, rankine: dict,
                     heat_balance: float, biogas_vol: float,
                     elec_power: float, hydrochar: float):
    """Store a calculation result in the database."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO calculations "
        "(timestamp, feedstock, inputs, otto_results, rankine_results, "
        " heat_balance, biogas_vol, elec_power, hydrochar) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            datetime.now().isoformat(),
            feedstock,
            json.dumps(inputs),
            json.dumps(otto),
            json.dumps(rankine),
            heat_balance,
            biogas_vol,
            elec_power,
            hydrochar,
        ),
    )
    conn.commit()
    conn.close()


def get_calculation_history(limit: int = 50):
    """Return recent calculations, newest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM calculations ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        d["inputs"] = json.loads(d["inputs"])
        d["otto_results"] = json.loads(d["otto_results"])
        d["rankine_results"] = json.loads(d["rankine_results"])
        results.append(d)
    return results


# Initialise on import
init_db()

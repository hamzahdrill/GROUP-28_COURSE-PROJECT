"""
FastAPI backend for the AD-HTC Biorefinery Dashboard.

Endpoints:
  GET  /              — serves the HTML dashboard
  GET  /api/feedstocks — returns all feedstock data from SQLite
  POST /api/analyze    — runs cycle calculations, stores results, returns JSON
  GET  /api/history    — returns past calculation results
"""

import math
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from models import (
    AnalysisInput, AnalysisResult, FeedstockOut,
    OttoResults, RankineResults, MassBalance, HeatIntegration,
)
from database import (
    get_all_feedstocks, get_feedstock_by_key,
    save_calculation, get_calculation_history,
)

# ═══════════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════════
app = FastAPI(
    title="AD-HTC Biorefinery Dashboard API",
    description="MEG 315 — Applied Thermodynamics · Group 28",
    version="2.0.0",
)

BASE_DIR = Path(__file__).parent

# ═══════════════════════════════════════════════════════════════
# STEAM TABLE DATA (P = 6.0 MPa / 60 bar)
# ═══════════════════════════════════════════════════════════════
STEAM_60BAR = [
    {"T": 275.59, "v": 0.03245, "u": 2589.9, "h": 2784.6, "s": 5.8902},
    {"T": 300,    "v": 0.03619, "u": 2668.4, "h": 2885.6, "s": 6.0703},
    {"T": 350,    "v": 0.04225, "u": 2790.4, "h": 3043.9, "s": 6.3357},
    {"T": 400,    "v": 0.04742, "u": 2893.7, "h": 3178.3, "s": 6.5432},
    {"T": 450,    "v": 0.05217, "u": 2989.9, "h": 3302.9, "s": 6.7219},
    {"T": 500,    "v": 0.05667, "u": 3083.1, "h": 3423.1, "s": 6.8826},
    {"T": 550,    "v": 0.06102, "u": 3175.2, "h": 3541.3, "s": 7.0308},
    {"T": 600,    "v": 0.06527, "u": 3267.2, "h": 3658.8, "s": 7.1693},
    {"T": 700,    "v": 0.07355, "u": 3453.0, "h": 3894.3, "s": 7.4247},
    {"T": 800,    "v": 0.08165, "u": 3643.2, "h": 4133.1, "s": 7.6582},
]

SAT_TABLE = [
    {"p": 0.01, "hf": 191.8, "hg": 2584.7, "sf": 0.649, "sg": 8.150},
    {"p": 0.02, "hf": 251.4, "hg": 2609.7, "sf": 0.832, "sg": 7.909},
    {"p": 0.04, "hf": 317.6, "hg": 2636.8, "sf": 1.026, "sg": 7.670},
    {"p": 0.06, "hf": 359.9, "hg": 2653.6, "sf": 1.145, "sg": 7.533},
    {"p": 0.08, "hf": 391.7, "hg": 2665.3, "sf": 1.233, "sg": 7.435},
    {"p": 0.10, "hf": 417.4, "hg": 2675.5, "sf": 1.303, "sg": 7.359},
    {"p": 0.20, "hf": 504.7, "hg": 2706.7, "sf": 1.530, "sg": 7.127},
    {"p": 0.50, "hf": 640.2, "hg": 2748.7, "sf": 1.861, "sg": 6.821},
    {"p": 1.00, "hf": 762.8, "hg": 2778.1, "sf": 2.139, "sg": 6.586},
]


def _interp_steam(T_C: float) -> dict:
    """Interpolate superheated steam properties at P=60 bar."""
    tbl = STEAM_60BAR
    Tc = max(tbl[0]["T"], min(tbl[-1]["T"], T_C))
    for i in range(len(tbl) - 1):
        if tbl[i]["T"] <= Tc <= tbl[i + 1]["T"]:
            f = (Tc - tbl[i]["T"]) / (tbl[i + 1]["T"] - tbl[i]["T"])
            return {
                k: tbl[i][k] + f * (tbl[i + 1][k] - tbl[i][k])
                for k in ("h", "s", "v", "u")
            }
    return {k: tbl[-1][k] for k in ("h", "s", "v", "u")}


def _sat_lookup(p_bar: float) -> dict:
    """Interpolate saturated water/steam properties."""
    tbl = SAT_TABLE
    if p_bar <= tbl[0]["p"]:
        return {**tbl[0]}
    if p_bar >= tbl[-1]["p"]:
        return {**tbl[-1]}
    for i in range(len(tbl) - 1):
        if tbl[i]["p"] <= p_bar <= tbl[i + 1]["p"]:
            f = (p_bar - tbl[i]["p"]) / (tbl[i + 1]["p"] - tbl[i]["p"])
            lerp = lambda a, b: a + f * (b - a)
            return {
                "hf": lerp(tbl[i]["hf"], tbl[i + 1]["hf"]),
                "hg": lerp(tbl[i]["hg"], tbl[i + 1]["hg"]),
                "sf": lerp(tbl[i]["sf"], tbl[i + 1]["sf"]),
                "sg": lerp(tbl[i]["sg"], tbl[i + 1]["sg"]),
            }
    return {**tbl[-1]}


# ═══════════════════════════════════════════════════════════════
# CALCULATION ENGINE
# ═══════════════════════════════════════════════════════════════

def run_cycle_analysis(inp: AnalysisInput, bm: dict) -> AnalysisResult:
    """Run full AD-HTC cycle analysis and return structured results."""

    # ── Mass balance ──
    feed_kg = inp.feed_rate * 1000
    vs_mass = feed_kg * bm["ts"] * bm["vs"]
    biogas_vol = vs_mass * bm["biogas_yield"]
    methane_vol = biogas_vol * bm["ch4"]
    biogas_mass = biogas_vol * 1.2
    digestate_dry = vs_mass * 0.40
    digestate_wet = feed_kg - biogas_mass
    hydrochar_kg = digestate_dry * bm["htc_yield"]

    # ── Otto cycle (air-standard) ──
    cp_air, cp_gas, gamma = 1.005, 1.148, 1.4
    T1, r, T3 = inp.T1, inp.compression_ratio, inp.T3

    T2 = T1 * r ** (gamma - 1)
    T4 = T3 / r ** (gamma - 1)
    W_comp = cp_air * (T2 - T1)
    W_turb = cp_gas * (T3 - T4)
    W_net = W_turb - W_comp
    Q_in = cp_gas * (T3 - T2)
    eta_otto = W_net / Q_in
    elec_power = inp.mass_flow_air * W_net
    therm_power = inp.mass_flow_air * cp_gas * (T4 - T1) * 0.45

    s1 = 1.0
    s2 = s1  # isentropic
    s3 = s2 + cp_gas * math.log(T3 / T2)
    s4 = s3  # isentropic

    # ── Rankine cycle (P = 60 bar fixed) ──
    sat = _sat_lookup(inp.p_cond)
    hA = sat["hf"]
    sA = sat["sf"]
    hfg = sat["hg"] - sat["hf"]
    sfg = sat["sg"] - sat["sf"]

    p_boiler = 60.0  # bar, fixed
    v_f = 0.001
    w_pump = v_f * (p_boiler - inp.p_cond) * 100
    hB = hA + w_pump / inp.eta_pump
    sB = sA

    stm = _interp_steam(inp.t_steam_C)
    hC = stm["h"]
    sC = stm["s"]

    x_s = min(1.0, (sC - sat["sf"]) / sfg)
    hDs = sat["hf"] + x_s * hfg
    hD = hC - inp.eta_turbine * (hC - hDs)
    x_act = min(1.0, max(0.0, (hD - sat["hf"]) / hfg))
    sD = sat["sf"] + x_act * sfg

    w_net_rank = (hC - hD) - w_pump / inp.eta_pump
    q_boiler = hC - hB
    eta_rank = w_net_rank / q_boiler if q_boiler > 0 else 0

    # ── Heat integration ──
    T_AD = 37
    Q_AD_kW = (feed_kg / 86400) * 4180 * (T_AD - (T1 - 273.15)) / 1000
    Q_HTC_kW = (digestate_wet / 86400) * 4000 * (inp.htc_temp - T_AD) / 1000
    heat_balance = therm_power - Q_AD_kW - Q_HTC_kW

    # ── OLR ──
    HRT = 25
    V_reactor = (feed_kg / 1000) * HRT
    olr = vs_mass / V_reactor if V_reactor > 0 else 0

    # ── Build response ──
    feedstock_out = FeedstockOut(
        id=bm["id"], key=bm["key"], name=bm["name"],
        ts=bm["ts"], vs=bm["vs"], biogas_yield=bm["biogas_yield"],
        ch4=bm["ch4"], htc_yield=bm["htc_yield"], htc_hhv=bm["htc_hhv"],
    )

    return AnalysisResult(
        feedstock=feedstock_out,
        otto=OttoResults(
            T1=T1, T2=round(T2, 2), T3=T3, T4=round(T4, 2),
            s1=s1, s2=s2, s3=round(s3, 4), s4=round(s4, 4),
            W_comp=round(W_comp, 2), W_turb=round(W_turb, 2),
            W_net=round(W_net, 2), Q_in=round(Q_in, 2),
            efficiency=round(eta_otto, 4),
            elec_power_kW=round(elec_power, 2),
            therm_power_kW=round(therm_power, 2),
        ),
        rankine=RankineResults(
            hA=round(hA, 2), sA=round(sA, 4),
            hB=round(hB, 2), sB=round(sB, 4),
            hC=round(hC, 2), sC=round(sC, 4),
            hD=round(hD, 2), sD=round(sD, 4),
            w_pump=round(w_pump, 2), w_net=round(w_net_rank, 2),
            q_boiler=round(q_boiler, 2), efficiency=round(eta_rank, 4),
            x_actual=round(x_act, 4),
        ),
        mass_balance=MassBalance(
            feed_kg=feed_kg, vs_mass=round(vs_mass, 1),
            biogas_vol=round(biogas_vol, 1), methane_vol=round(methane_vol, 1),
            biogas_mass=round(biogas_mass, 1),
            digestate_dry=round(digestate_dry, 1),
            digestate_wet=round(digestate_wet, 1),
            hydrochar_kg=round(hydrochar_kg, 1),
        ),
        heat=HeatIntegration(
            therm_power_kW=round(therm_power, 2),
            Q_AD_kW=round(Q_AD_kW, 2),
            Q_HTC_kW=round(Q_HTC_kW, 2),
            heat_balance_kW=round(heat_balance, 2),
            status="SURPLUS" if heat_balance >= 0 else "DEFICIT",
        ),
        olr=round(olr, 3),
    )


# ═══════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the main dashboard HTML."""
    html_path = BASE_DIR / "ad-htc-biomass-v2.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/api/feedstocks", response_model=list[FeedstockOut])
async def list_feedstocks():
    """Return all 12 feedstock types from the database."""
    return get_all_feedstocks()


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze(inp: AnalysisInput):
    """Run full AD-HTC cycle analysis and store in database."""
    bm = get_feedstock_by_key(inp.feedstock_key)
    if not bm:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Feedstock '{inp.feedstock_key}' not found")

    result = run_cycle_analysis(inp, bm)

    # Store in database
    save_calculation(
        feedstock=inp.feedstock_key,
        inputs=inp.model_dump(),
        otto=result.otto.model_dump(),
        rankine=result.rankine.model_dump(),
        heat_balance=result.heat.heat_balance_kW,
        biogas_vol=result.mass_balance.biogas_vol,
        elec_power=result.otto.elec_power_kW,
        hydrochar=result.mass_balance.hydrochar_kg,
    )

    return result


@app.get("/api/history")
async def history(limit: int = 50):
    """Return past calculation results from the database."""
    return get_calculation_history(limit)


# ═══════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

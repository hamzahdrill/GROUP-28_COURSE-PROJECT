"""
Pydantic models for the AD-HTC Biorefinery API.
"""

from pydantic import BaseModel, Field
from typing import Optional


class AnalysisInput(BaseModel):
    """Input parameters from the dashboard sidebar."""
    feedstock_key: str = Field(..., description="Biomass type key (e.g. 'cow_manure')")
    feed_rate: float = Field(10.0, description="Feed rate in tonnes/day")
    T1: float = Field(298.0, description="Otto cycle intake temperature (K)")
    compression_ratio: float = Field(10.0, description="Compression ratio r")
    T3: float = Field(1200.0, description="Peak combustion temperature (K)")
    mass_flow_air: float = Field(50.0, description="Air mass flow rate (kg/s)")
    t_steam_C: float = Field(500.0, description="Steam temperature (°C)")
    p_cond: float = Field(0.06, description="Condenser pressure (bar)")
    eta_turbine: float = Field(0.85, description="Steam turbine efficiency")
    eta_pump: float = Field(0.80, description="Pump efficiency")
    htc_temp: float = Field(220.0, description="HTC reactor temperature (°C)")


class FeedstockOut(BaseModel):
    """Feedstock data returned from the database."""
    id: int
    key: str
    name: str
    ts: float
    vs: float
    biogas_yield: float
    ch4: float
    htc_yield: float
    htc_hhv: float


class OttoResults(BaseModel):
    """Otto cycle calculation results."""
    T1: float
    T2: float
    T3: float
    T4: float
    s1: float
    s2: float
    s3: float
    s4: float
    W_comp: float
    W_turb: float
    W_net: float
    Q_in: float
    efficiency: float
    elec_power_kW: float
    therm_power_kW: float


class RankineResults(BaseModel):
    """Rankine cycle calculation results."""
    hA: float
    sA: float
    hB: float
    sB: float
    hC: float
    sC: float
    hD: float
    sD: float
    w_pump: float
    w_net: float
    q_boiler: float
    efficiency: float
    x_actual: float


class MassBalance(BaseModel):
    """Daily mass balance outputs."""
    feed_kg: float
    vs_mass: float
    biogas_vol: float
    methane_vol: float
    biogas_mass: float
    digestate_dry: float
    digestate_wet: float
    hydrochar_kg: float


class HeatIntegration(BaseModel):
    """Heat integration results."""
    therm_power_kW: float
    Q_AD_kW: float
    Q_HTC_kW: float
    heat_balance_kW: float
    status: str  # "SURPLUS" or "DEFICIT"


class AnalysisResult(BaseModel):
    """Complete analysis response."""
    feedstock: FeedstockOut
    otto: OttoResults
    rankine: RankineResults
    mass_balance: MassBalance
    heat: HeatIntegration
    olr: float

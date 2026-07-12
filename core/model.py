from __future__ import annotations
from dataclasses import dataclass, asdict
from math import exp
from typing import Dict, Iterable, List, Tuple
import numpy as np

HHV_KWH_KG_H2 = 39.41
LHV_KWH_KG_H2 = 33.33
WATER_KG_KG_H2 = 9.0
OXYGEN_KG_KG_H2 = 8.0
CP_LIQ_KWH_KG_K = 4.18 / 3600.0
CP_STEAM_KWH_KG_K = 2.08 / 3600.0
LATENT_KWH_KG = 2.257 / 3.6

@dataclass
class Inputs:
    flow_m3_day: float
    water_recovery_pct: float
    desal_kwh_m3: float
    salt_recovery_pct: float
    feed_temp_c: float
    steam_temp_c: float
    reactor_temp_c: float
    pressure_bar: float
    plasma_power_kw: float
    hours_day: float
    plasma_eff_pct: float
    thermal_recovery_pct: float
    argon_pct: float
    argon_recovery_pct: float
    renewable_pct: float
    residual_grid_g_kwh: float
    benchmark_kwh_kg: float
    carbon_feed_kg_h: float
    carbon_capture_pct: float
    solid_carbon_yield_pct: float
    sal: float
    cl: float
    so4: float
    mg: float
    ca: float
    hco3: float
    boron: float
    silica: float
    bromide: float


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def calculate(i: Inputs) -> Dict[str, float]:
    clean_m3 = i.flow_m3_day * i.water_recovery_pct / 100.0
    brine_m3 = max(0.0, i.flow_m3_day - clean_m3)
    salt_kg_day = i.flow_m3_day * i.sal * i.salt_recovery_pct / 100.0
    desal_kwh = i.flow_m3_day * i.desal_kwh_m3

    conductivity = clamp(i.sal / 35.0, 0.0, 1.6)
    chloride_risk = clamp((i.cl / 19.4) + 0.5 * (i.bromide / 0.067 if i.bromide else 0.0), 0.0, 3.0)
    scaling = clamp((i.mg/1.29 + i.ca/0.41 + i.hco3/0.14 + i.silica/0.003 if i.silica else i.mg/1.29+i.ca/0.41+i.hco3/0.14)/4.0,0.0,3.0)
    boron_index = clamp(i.boron / 0.0045 if i.boron else 0.0, 0.0, 3.0)
    pretreatment = 1.0 + 0.07*chloride_risk + 0.06*scaling + 0.015*boron_index

    dt_liq=max(0.0,100.0-i.feed_temp_c)
    dt_steam=max(0.0,i.steam_temp_c-100.0)
    steam_heat_per_kg = CP_LIQ_KWH_KG_K*dt_liq + LATENT_KWH_KG + CP_STEAM_KWH_KG_K*dt_steam

    plasma_kwh=i.plasma_power_kw*i.hours_day
    useful_plasma=plasma_kwh*i.plasma_eff_pct/100.0
    temp_activation=clamp(1.0-exp(-(max(i.reactor_temp_c,500)-500)/3000.0),0.0,0.96)
    pressure_factor=clamp(1.0-0.0065*max(i.pressure_bar-1.0,0.0),0.62,1.0)
    argon_factor=1.0+0.07*clamp(i.argon_pct/30.0,0.0,1.6)
    ionic_penalty=clamp(1.0-0.075*chloride_risk-0.05*scaling,0.50,1.0)
    process_factor=clamp((0.70+0.38*temp_activation)*pressure_factor*argon_factor*ionic_penalty,0.30,1.18)

    energy_limited=useful_plasma*process_factor/HHV_KWH_KG_H2
    water_limited=clean_m3*1000.0/WATER_KG_KG_H2
    h2=min(energy_limited,water_limited)
    water_used=h2*WATER_KG_KG_H2
    oxygen=h2*OXYGEN_KG_KG_H2
    steam_kwh=water_used*steam_heat_per_kg*pretreatment
    argon_makeup=max(0.0,1.0-i.argon_recovery_pct/100.0)
    argon_aux=plasma_kwh*(i.argon_pct/100.0)*argon_makeup*0.035
    recovered=plasma_kwh*i.thermal_recovery_pct/100.0
    gross=plasma_kwh+desal_kwh+steam_kwh+argon_aux
    net=max(0.0,gross-recovered)
    sec=net/h2 if h2>0 else 0.0
    eff=100.0*HHV_KWH_KG_H2/sec if sec>0 else 0.0

    residual=(1.0-i.renewable_pct/100.0)*i.residual_grid_g_kwh
    co2=net*residual/1000.0
    benchmark_co2=h2*i.benchmark_kwh_kg*residual/1000.0
    avoided=benchmark_co2-co2

    solid=(i.carbon_feed_kg_h*i.hours_day*i.carbon_capture_pct/100.0*i.solid_carbon_yield_pct/100.0)

    alerts=[]
    if chloride_risk>0.9: alerts.append('High halide index: corrosion and chlorine/bromine side-reaction controls are required.')
    if scaling>0.9: alerts.append('Scaling index is high: Mg/Ca/bicarbonate/silica pretreatment must be reviewed.')
    if sec>i.benchmark_kwh_kg: alerts.append('Current model consumes more electricity per kg H2 than the selected benchmark.')
    if avoided<0: alerts.append('Operational climate result is worse than the selected benchmark under the current electricity mix.')
    if i.renewable_pct<70: alerts.append('Low renewable share strongly limits climate performance.')
    if eff>100: alerts.append('HHV efficiency exceeds 100%; review system boundary and heat-credit assumptions.')

    return {
      **asdict(i), 'clean_m3_day':clean_m3,'brine_m3_day':brine_m3,'salt_kg_day':salt_kg_day,
      'desal_kwh_day':desal_kwh,'steam_kwh_day':steam_kwh,'plasma_kwh_day':plasma_kwh,
      'argon_aux_kwh_day':argon_aux,'recovered_kwh_day':recovered,'net_kwh_day':net,
      'h2_kg_day':h2,'oxygen_kg_day':oxygen,'water_used_kg_day':water_used,
      'sec_kwh_kg':sec,'hhv_eff_pct':eff,'co2_kg_day':co2,'avoided_co2_kg_day':avoided,
      'solid_carbon_kg_day':solid,'conductivity_index':conductivity,'halide_risk':chloride_risk,
      'scaling_index':scaling,'boron_index':boron_index,'temp_activation':temp_activation,
      'process_factor':process_factor,'alerts':alerts,
    }


def timeseries(i: Inputs, result: Dict[str,float], points: int = 96) -> Dict[str,List[float]]:
    t=np.linspace(0,24,points)
    load=0.92+0.07*np.sin((t-5)*np.pi/12)+0.025*np.sin(t*np.pi/2)
    temp=i.reactor_temp_c*(0.985+0.015*np.sin((t-2)*np.pi/6))
    pressure=i.pressure_bar*(0.99+0.01*np.sin(t*np.pi/4))
    h2=(result['h2_kg_day']/24.0)*load
    sec=result['sec_kwh_kg']*(1.0+0.025*np.cos(t*np.pi/5))
    return {'hour':t.tolist(),'temperature_c':temp.tolist(),'pressure_bar':pressure.tolist(),'h2_kg_h':h2.tolist(),'sec_kwh_kg':sec.tolist()}


def compare_profiles(base: Inputs, profiles: Dict[str,dict]) -> List[dict]:
    rows=[]
    for name,p in profiles.items():
        d=asdict(base); d.update(p); r=calculate(Inputs(**d)); rows.append({'profile':name,**r})
    return rows


def sensitivity(base: Inputs, parameter: str, values: Iterable[float]) -> List[dict]:
    out=[]
    for v in values:
        d=asdict(base); d[parameter]=float(v); r=calculate(Inputs(**d));
        out.append({'value':float(v),'h2_kg_day':r['h2_kg_day'],'sec_kwh_kg':r['sec_kwh_kg'],'hhv_eff_pct':r['hhv_eff_pct'],'avoided_co2_kg_day':r['avoided_co2_kg_day']})
    return out


def optimize(base: Inputs) -> Tuple[dict|None,int]:
    best=None; tested=0
    for temp in range(3000,8501,500):
      for thermal in range(20,81,10):
       for argon in range(0,51,10):
        for eff in range(45,86,10):
          tested+=1
          d=asdict(base); d.update(reactor_temp_c=float(temp),thermal_recovery_pct=float(thermal),argon_pct=float(argon),plasma_eff_pct=float(eff))
          r=calculate(Inputs(**d))
          if r['sec_kwh_kg']<=0 or r['hhv_eff_pct']>100: continue
          penalty=max(0.0,r['sec_kwh_kg']-base.benchmark_kwh_kg)*4.0 + r['halide_risk']*5 + r['scaling_index']*3
          score=r['h2_kg_day'] + 0.12*r['avoided_co2_kg_day'] - penalty
          if best is None or score>best['score']: best={'score':score,'inputs':d,'result':r}
    return best,tested


def reliability_map() -> Dict[str,dict]:
    return {
      'Hydrogen and oxygen stoichiometry': {'level':'Consolidated','color':'#48c76b','basis':'2 H2O -> 2 H2 + O2'},
      'Water heating and vaporization': {'level':'Engineering estimate','color':'#19c7ff','basis':'Sensible + latent + superheat duty'},
      'Plasma conversion factor': {'level':'Scenario model','color':'#ff9a3c','basis':'Calibratable activation and loss factors'},
      'Seawater chemistry influence': {'level':'Scenario model','color':'#ff9a3c','basis':'Screening indices, not reaction kinetics'},
      'Graphene / nanotube formation': {'level':'Research hypothesis','color':'#ff5e68','basis':'Requires carbon feed, catalyst and material characterization'},
      'Climate benefit': {'level':'Scenario model','color':'#ff9a3c','basis':'Operational electricity inventory, not full LCA'},
    }

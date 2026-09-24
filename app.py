import json
from dataclasses import asdict
from pathlib import Path
import pandas as pd
import streamlit as st
from core.model import Inputs, calculate, timeseries, compare_profiles, sensitivity, optimize, reliability_map
from core.reporting import build_pdf
from views.style import inject_style
from views.charts import digital_twin_3d, sankey, live_timeseries, scenario_bars, radar, sensitivity_chart

st.set_page_config(page_title='HydrogenOrg Integrated Climate & Hydrogen Simulator V3.2',page_icon='⚡',layout='wide',initial_sidebar_state='expanded')
inject_style()

# NAV-02: native navigation links, available in every workspace.
st.link_button('← Back to HydrogenOrg', 'https://hydrogenorg.ch/', type='primary', help='Opens the website in a new tab and keeps this simulation available.')
st.caption('Navigation update · NAV-02')
st.sidebar.link_button('← Back to HydrogenOrg', 'https://hydrogenorg.ch/', help='Opens the website in a new tab.')
PROFILES=json.loads((Path(__file__).parent/'data'/'water_profiles.json').read_text(encoding='utf-8'))

st.sidebar.markdown('## HYDROGENORG')
st.sidebar.caption('Integrated Climate & Hydrogen Simulator V3.2')
mode=st.sidebar.segmented_control('View mode',['Research','Engineering','Executive'],default='Research')
page=st.sidebar.radio('Workspace',['Mission Control','Interactive 3D Digital Twin','Energy & Matter Sankey','Live Analytics','Scenario Laboratory','Sensitivity Lab','Optimization Engine','Water Chemistry','Scientific Basis','Technical Report','Research Limits'])
profile_name=st.sidebar.selectbox('Water profile',list(PROFILES.keys()),index=4); wp=PROFILES[profile_name]

st.sidebar.markdown('### Water and desalination')
flow=st.sidebar.number_input('Feedwater (m3/day)',1.0,100000.0,1000.0,10.0)
water_rec=st.sidebar.slider('Clean-water recovery (%)',10,95,45)
desal=st.sidebar.number_input('Desalination electricity (kWh/m3 feed)',0.0,30.0,3.5,0.1)
salt_rec=st.sidebar.slider('Salt/mineral recovery (%)',0,95,60)
feed_t=st.sidebar.slider('Feedwater temperature (C)',0,45,20)
steam_t=st.sidebar.slider('Steam temperature (C)',100,1200,350,10)

st.sidebar.markdown('### Plasma reactor')
reactor_t=st.sidebar.slider('Reactor temperature (C)',500,12000,5000,100)
pressure=st.sidebar.slider('Pressure (bar)',1.0,40.0,6.0,0.5)
power=st.sidebar.number_input('Plasma electrical power (kW)',10.0,100000.0,1000.0,10.0)
hours=st.sidebar.slider('Operating hours/day',1.0,24.0,20.0,0.5)
plasma_eff=st.sidebar.slider('Electrical-to-useful-plasma efficiency (%)',10,95,65)
thermal=st.sidebar.slider('Thermal recovery (%)',0,90,45)
argon=st.sidebar.slider('Argon fraction in gas loop (%)',0,80,20)
argon_rec=st.sidebar.slider('Argon recovery (%)',0,99,90)

st.sidebar.markdown('### Climate and benchmark')
renew=st.sidebar.slider('Renewable electricity share (%)',0,100,90)
grid=st.sidebar.number_input('Residual grid intensity (g CO2/kWh)',0.0,1200.0,80.0,10.0)
benchmark=st.sidebar.number_input('Benchmark electricity (kWh/kg H2)',20.0,100.0,52.0,0.5)

st.sidebar.markdown('### Optional carbon pathway')
carbon_feed=st.sidebar.number_input('Carbon-bearing feed (kg/h as C equivalent)',0.0,10000.0,0.0,1.0)
carbon_capture=st.sidebar.slider('Carbon capture efficiency (%)',0,100,0)
solid_yield=st.sidebar.slider('Solid-carbon yield (%)',0,100,0)

i=Inputs(flow,water_rec,desal,salt_rec,feed_t,steam_t,reactor_t,pressure,power,hours,plasma_eff,thermal,argon,argon_rec,renew,grid,benchmark,carbon_feed,carbon_capture,solid_yield,**wp)
r=calculate(i); comp=compare_profiles(i,PROFILES); rel=reliability_map()

st.markdown('<div class="topbar"><div class="brand">HYDROGEN<span>ORG.CH</span> · INTEGRATED RESEARCH SIMULATOR V3.2</div><div class="sys">SYSTEM ONLINE · MODEL TRANSPARENT · VALIDATION REQUIRED</div></div>',unsafe_allow_html=True)

if page=='Mission Control':
 st.markdown('''<div class="hero"><div><div class="kicker">HydrogenOrg integrated research platform V3.2</div><div class="title">Water, Plasma, Hydrogen and <span>Climate Intelligence.</span></div><div class="lead">A redesigned research, engineering and executive environment with an interactive 3D reactor twin, energy and matter Sankey, live analytics, multi-scenario comparison, sensitivity, constrained optimization and technical reporting.</div></div><div class="hero-panel"><b>Transparent before persuasive.</b><p>Every result is labelled as consolidated, engineering estimate, scenario model or research hypothesis.</p></div></div>''',unsafe_allow_html=True)
 st.markdown(f'''<div class="metrics"><div class="metric"><small>Hydrogen output</small><strong>{r['h2_kg_day']:.2f} kg/day</strong><em>Energy and water constrained</em></div><div class="metric"><small>Net electricity</small><strong>{r['sec_kwh_kg']:.1f} kWh/kg</strong><em>Full operating boundary</em></div><div class="metric"><small>HHV efficiency</small><strong>{r['hhv_eff_pct']:.1f}%</strong><em>Boundary dependent</em></div><div class="metric"><small>Climate delta</small><strong>{r['avoided_co2_kg_day']:.1f} kg CO2/day</strong><em>Vs selected benchmark</em></div></div>''',unsafe_allow_html=True)
 if mode=='Executive':
  c1,c2=st.columns([1.2,.8]);
  with c1: st.plotly_chart(scenario_bars(comp),width='stretch')
  with c2:
   st.markdown('### Decision summary')
   st.metric('Salt/mineral recovery',f"{r['salt_kg_day']:.0f} kg/day")
   st.metric('Operational CO2',f"{r['co2_kg_day']:.1f} kg/day")
   st.metric('Chemistry risk',f"{max(r['halide_risk'],r['scaling_index']):.2f}")
 else:
  st.plotly_chart(digital_twin_3d(r),width='stretch',config={'scrollZoom':True,'displaylogo':False,'modeBarButtonsToRemove':['lasso3d','select2d']})
  c1,c2=st.columns(2)
  with c1: st.plotly_chart(sankey(r),width='stretch')
  with c2: st.plotly_chart(live_timeseries(timeseries(i,r)),width='stretch')
 for a in r['alerts']: st.warning(a)
 st.markdown('<div class="section"><h2>Reliability map</h2><div class="reliability">'+''.join(f"<div class='rel'><b>{k}</b><span class='pill' style='background:{v['color']}22;color:{v['color']}'>{v['level']}</span><p>{v['basis']}</p></div>" for k,v in rel.items())+'</div></div>',unsafe_allow_html=True)

elif page=='Interactive 3D Digital Twin':
 st.markdown('## Interactive 3D Digital Twin')
 st.caption('The Digital Twin now opens already enlarged and centred. Use the mouse to rotate or refine the zoom; the Home icon restores the intended view.')
 st.plotly_chart(digital_twin_3d(r),width='stretch',config={'scrollZoom':True,'displaylogo':False,'modeBarButtonsToRemove':['lasso3d','select2d']})
 st.caption('Conceptual visualization. It is not a certified SCADA or industrial digital twin.')

elif page=='Energy & Matter Sankey':
 st.markdown('## Energy and matter Sankey')
 st.plotly_chart(sankey(r),width='stretch')
 st.dataframe(pd.DataFrame({'stream':['Hydrogen','Oxygen','Clean water','Brine','Recovered salt','Recovered heat'],'value':[r['h2_kg_day'],r['oxygen_kg_day'],r['clean_m3_day'],r['brine_m3_day'],r['salt_kg_day'],r['recovered_kwh_day']],'unit':['kg/day','kg/day','m3/day','m3/day','kg/day','kWh/day']}),width='stretch',hide_index=True)

elif page=='Live Analytics':
 st.markdown('## Live analytics')
 ts=timeseries(i,r); st.plotly_chart(live_timeseries(ts),width='stretch')
 c1,c2,c3,c4=st.columns(4); c1.metric('Temperature',f'{reactor_t} C'); c2.metric('Pressure',f'{pressure:.1f} bar'); c3.metric('H2 production',f"{r['h2_kg_day']/24:.2f} kg/h"); c4.metric('Recovered heat',f"{r['recovered_kwh_day']/24:.1f} kW avg")

elif page=='Scenario Laboratory':
 st.markdown('## Scenario laboratory')
 st.plotly_chart(scenario_bars(comp),width='stretch')
 st.plotly_chart(radar(comp),width='stretch')
 st.dataframe(pd.DataFrame(comp)[['profile','h2_kg_day','sec_kwh_kg','hhv_eff_pct','avoided_co2_kg_day','halide_risk','scaling_index']],width='stretch',hide_index=True)

elif page=='Sensitivity Lab':
 st.markdown('## Sensitivity laboratory')
 param=st.selectbox('Parameter',['reactor_temp_c','pressure_bar','thermal_recovery_pct','argon_pct','plasma_eff_pct','renewable_pct'])
 ranges={'reactor_temp_c':range(2000,9001,500),'pressure_bar':[1+i for i in range(20)],'thermal_recovery_pct':range(0,91,5),'argon_pct':range(0,61,5),'plasma_eff_pct':range(30,91,5),'renewable_pct':range(0,101,5)}
 rows=sensitivity(i,param,ranges[param]); st.plotly_chart(sensitivity_chart(rows,param),width='stretch'); st.dataframe(pd.DataFrame(rows),width='stretch',hide_index=True)

elif page=='Optimization Engine':
 st.markdown('## Constrained optimization engine')
 st.write('The optimizer searches the model space. It does not prove physical feasibility; experimental and engineering constraints must be added as evidence becomes available.')
 if st.button('Run optimization',type='primary'):
  best,tested=optimize(i); st.success(f'{tested} candidate configurations evaluated.')
  if best:
   br=best['result']; bi=best['inputs']; st.markdown(f'''<div class="metrics"><div class="metric"><small>Temperature</small><strong>{bi['reactor_temp_c']:.0f} C</strong></div><div class="metric"><small>Thermal recovery</small><strong>{bi['thermal_recovery_pct']:.0f}%</strong></div><div class="metric"><small>Argon fraction</small><strong>{bi['argon_pct']:.0f}%</strong></div><div class="metric"><small>Specific electricity</small><strong>{br['sec_kwh_kg']:.1f} kWh/kg</strong></div></div>''',unsafe_allow_html=True)
   st.json({'optimized_inputs':bi,'results':br})
  else: st.error('No feasible model configuration found.')

elif page=='Water Chemistry':
 st.markdown('## Water chemistry and process risk')
 c1,c2,c3,c4=st.columns(4); c1.metric('Salinity',f"{wp['sal']:.2f} g/L"); c2.metric('Halide risk',f"{r['halide_risk']:.2f}"); c3.metric('Scaling index',f"{r['scaling_index']:.2f}"); c4.metric('Conductivity index',f"{r['conductivity_index']:.2f}")
 st.dataframe(pd.DataFrame([{'species':k,'g/L':v} for k,v in wp.items()]),width='stretch',hide_index=True)
 st.warning('Higher conductivity can be beneficial, while chloride/bromide reactions, corrosion, scaling, silica deposition, catalyst poisoning and membrane degradation can be detrimental. The net effect is process-specific.')

elif page=='Scientific Basis':
 st.markdown('## Scientific basis, equations and confidence')
 eqs=[('Water splitting','2 H2O -> 2 H2 + O2','Consolidated'),('Water demand','m_H2O = 9 x m_H2','Consolidated'),('Oxygen co-product','m_O2 = 8 x m_H2','Consolidated'),('Steam duty','Q = m[c_p,liq(100-T0) + delta h_vap + c_p,steam(Tsteam-100)]','Engineering estimate'),('Specific electricity','SEC = E_net / m_H2','Mass and energy balance'),('HHV efficiency','eta_HHV = HHV_H2 / SEC','Boundary dependent'),('Operational emissions','CO2 = E_net x grid intensity x (1-renewable share)','Scenario inventory'),('Solid carbon','m_C,solid = carbon feed x capture x solid yield','Research hypothesis')]
 for n,e,s in eqs:
  with st.expander(n): st.markdown(f'<div class="eq">{e}</div>',unsafe_allow_html=True); st.caption(s)
 st.error('A carbon balance cannot identify graphite, graphene or nanotubes. Raman, TEM, XRD and other material characterization are required.')

elif page=='Technical Report':
 st.markdown('## Technical report and data export')
 pdf=build_pdf('HydrogenOrg Integrated Climate & Hydrogen Simulator V3.2',profile_name,asdict(i),r,comp,rel)
 st.download_button('Download technical PDF',pdf,'HydrogenOrg_V3_2_Technical_Report.pdf','application/pdf',type='primary')
 st.download_button('Download scenario JSON',json.dumps({'profile':profile_name,'inputs':asdict(i),'results':r,'comparisons':comp,'reliability':rel},indent=2),'HydrogenOrg_V3_2_Scenario.json','application/json')
 st.download_button('Download comparison CSV',pd.DataFrame(comp).to_csv(index=False).encode('utf-8'),'HydrogenOrg_V3_2_Comparison.csv','text/csv')

else:
 st.markdown('## Research limits and falsifiability')
 limits=[('Thermodynamics','Stoichiometric balances and standard hydrogen energy values are strong foundations.'),('Plasma kinetics','Reaction kinetics, residence time, non-equilibrium chemistry and plasma diagnostics require experiments.'),('Seawater chemistry','Risk indices do not replace corrosion, electrochemistry and plasma-chemistry testing.'),('Carbon nanomaterials','Graphene or nanotubes require a carbon-bearing feed, suitable catalysts and direct characterization.'),('Optimization','The optimizer finds the best point inside this model, not necessarily in physical reality.'),('Climate benefit','The model is an operational electricity inventory, not a complete life-cycle assessment.'),('Safety','Hydrogen, oxygen, high voltage, pressure, hot plasma and halogen chemistry require HAZOP and professional engineering review.')]
 for t,b in limits:
  with st.expander(t): st.write(b)

st.markdown('<div class="footer"><strong>HydrogenOrg scientific position</strong><p>The simulator is built to expose assumptions, compare scenarios, identify failure conditions and define experiments - not to convert hypotheses into claims.</p></div>',unsafe_allow_html=True)

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

DARK='#071421'; CYAN='#19c7ff'; GREEN='#62c945'; ORANGE='#ff8a3d'; MUTED='#91a7b7'

def _layout(fig,title):
    fig.update_layout(title=title,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(7,20,33,.96)',font=dict(color='#eaf6fb'),margin=dict(l=20,r=20,t=55,b=20),legend=dict(orientation='h'))
    fig.update_xaxes(gridcolor='rgba(255,255,255,.08)'); fig.update_yaxes(gridcolor='rgba(255,255,255,.08)')
    return fig

def digital_twin_3d(result):
    """Large, close-up 3D conceptual process twin with a corrected initial camera.

    The previous version relied on Plotly auto-ranging. Because the process pipes
    extended much farther than the reactor radius, Plotly reduced the reactor to a
    tiny object and overlapped the labels. This version uses explicit scene ranges,
    a manual aspect ratio and separated component positions.
    """
    fig = go.Figure()

    # Main plasma reactor cylinder.
    theta = np.linspace(0, 2 * np.pi, 96)
    z = np.linspace(0, 6.6, 64)
    T, Z = np.meshgrid(theta, z)
    radius = 3.15
    X = radius * np.cos(T)
    Y = radius * np.sin(T)
    fig.add_surface(
        x=X, y=Y, z=Z,
        colorscale=[[0, '#29175f'], [.42, '#7955e7'], [.72, '#19c7ff'], [1, '#62c945']],
        showscale=False,
        opacity=.78,
        hoverinfo='skip',
        name='Plasma reactor',
    )

    # Reactor rings and animated-looking plasma core.
    for zz, rr, color, width in [
        (0.0, 3.30, CYAN, 9),
        (6.6, 3.30, GREEN, 9),
        (3.3, 1.05, '#ffffff', 11),
    ]:
        fig.add_trace(go.Scatter3d(
            x=rr*np.cos(theta), y=rr*np.sin(theta), z=[zz]*len(theta),
            mode='lines', line=dict(color=color, width=width),
            hoverinfo='skip', showlegend=False,
        ))

    # Process nodes are deliberately separated in y and z to avoid text overlap.
    nodes = [
        (-6.8, 0.0, 3.3, 'STEAM + Ar', CYAN),
        ( 6.8, 0.0, 3.3, 'H₂ SEPARATION', GREEN),
        ( 0.0, 0.0,-2.6, 'HEAT RECOVERY', ORANGE),
    ]
    for x0, y0, z0, label, color in nodes:
        fig.add_trace(go.Scatter3d(
            x=[x0], y=[y0], z=[z0], mode='markers+text',
            text=[label], textposition='top center',
            marker=dict(size=18, color=color, line=dict(color='#eef7fb', width=2)),
            textfont=dict(size=14, color='#eef7fb'),
            hovertemplate=f'{label}<extra></extra>',
            showlegend=False,
        ))

    # Flow lines.
    flows = [
        ([-6.55, -3.45], [0, 0], [3.3, 3.3], CYAN),
        ([ 3.45,  6.55], [0, 0], [3.3, 3.3], GREEN),
        ([ 0.0,  0.0], [0, 0], [0.0,-2.25], ORANGE),
    ]
    for xs, ys, zs, color in flows:
        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=zs, mode='lines',
            line=dict(color=color, width=12),
            hoverinfo='skip', showlegend=False,
        ))

    # Reactor label placed above the equipment, not inside other labels.
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[7.45], mode='text',
        text=['PLASMA REACTOR'], textfont=dict(size=16, color='#eef7fb'),
        hoverinfo='skip', showlegend=False,
    ))

    fig.update_layout(
        title=dict(
            text=(
                f"Interactive reactor twin — {result['reactor_temp_c']:.0f} °C | "
                f"{result['pressure_bar']:.1f} bar | {result['h2_kg_day']:.1f} kg/day H₂"
            ),
            x=.01, xanchor='left', y=.98,
            font=dict(size=18, color='#eef7fb'),
        ),
        scene=dict(
            bgcolor=DARK,
            xaxis=dict(visible=False, range=[-7.8, 7.8]),
            yaxis=dict(visible=False, range=[-3.7, 3.7]),
            zaxis=dict(visible=False, range=[-3.4, 8.2]),
            aspectmode='manual',
            aspectratio=dict(x=1.85, y=0.88, z=1.28),
            camera=dict(eye=dict(x=0.92, y=1.02, z=0.72), center=dict(x=0, y=0, z=0.08), up=dict(x=0, y=0, z=1)),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=70, b=0),
        height=720,
        font=dict(color='#eef7fb'),
        uirevision='hydrogenorg-v3-2-twin',
    )
    return fig

def sankey(result):
    labels=['Electricity','Seawater','Plasma reactor','Desalination','Steam duty','Hydrogen','Oxygen','Recovered heat','Brine/salts','Losses']
    source=[0,1,0,0,2,2,2,2,3,4]; target=[2,3,3,4,5,6,7,9,8,9]
    vals=[result['plasma_kwh_day'],result['flow_m3_day'],result['desal_kwh_day'],result['steam_kwh_day'],result['h2_kg_day']*39.41,result['oxygen_kg_day']*2,result['recovered_kwh_day'],max(1,result['net_kwh_day']*0.08),result['salt_kg_day'],max(1,result['steam_kwh_day']*.12)]
    fig=go.Figure(go.Sankey(node=dict(label=labels,pad=18,thickness=18,color=['#19c7ff','#278fd1','#845ee6','#3ba0d8','#ff8a3d','#62c945','#6ac8ff','#f07c29','#d7c680','#ff5e68']),link=dict(source=source,target=target,value=vals,color='rgba(25,199,255,.22)')))
    return _layout(fig,'Energy and matter Sankey')

def live_timeseries(ts):
    df=pd.DataFrame(ts)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df.hour,y=df.temperature_c,name='Temperature C',line=dict(color='#845ee6',width=3),yaxis='y'))
    fig.add_trace(go.Scatter(x=df.hour,y=df.h2_kg_h,name='H2 kg/h',line=dict(color=GREEN,width=3),yaxis='y2'))
    fig.update_layout(yaxis=dict(title='Temperature C'),yaxis2=dict(title='H2 kg/h',overlaying='y',side='right'))
    return _layout(fig,'24-hour simulated operating profile')

def scenario_bars(rows):
    df=pd.DataFrame(rows)
    fig=px.bar(df,x='profile',y='sec_kwh_kg',color='h2_kg_day',color_continuous_scale=['#19c7ff','#62c945'],labels={'sec_kwh_kg':'kWh/kg H2','h2_kg_day':'H2 kg/day'})
    return _layout(fig,'Water-profile scenario comparison')

def radar(rows):
    traces=[]
    for r in rows:
        theta=['H2 output','HHV efficiency','Heat recovery','Climate delta','Low chemistry risk']
        vals=[r['h2_kg_day']/max(x['h2_kg_day'] for x in rows)*100,r['hhv_eff_pct'],r['thermal_recovery_pct'],max(0,50+r['avoided_co2_kg_day']),max(0,100-25*r['halide_risk']-15*r['scaling_index'])]
        traces.append(go.Scatterpolar(r=vals+[vals[0]],theta=theta+[theta[0]],fill='toself',name=r['profile']))
    fig=go.Figure(traces); fig.update_layout(polar=dict(bgcolor=DARK,radialaxis=dict(range=[0,100],gridcolor='rgba(255,255,255,.12)')),showlegend=True)
    return _layout(fig,'Multi-criteria scenario radar')

def sensitivity_chart(rows,param):
    df=pd.DataFrame(rows)
    fig=go.Figure(); fig.add_trace(go.Scatter(x=df.value,y=df.sec_kwh_kg,name='kWh/kg H2',line=dict(color=CYAN,width=3))); fig.add_trace(go.Scatter(x=df.value,y=df.h2_kg_day,name='H2 kg/day',line=dict(color=GREEN,width=3),yaxis='y2'))
    fig.update_layout(yaxis=dict(title='kWh/kg H2'),yaxis2=dict(title='H2 kg/day',overlaying='y',side='right'))
    return _layout(fig,f'Sensitivity: {param}')

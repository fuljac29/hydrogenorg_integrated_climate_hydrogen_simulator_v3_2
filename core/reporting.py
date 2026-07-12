from io import BytesIO
from datetime import datetime, timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak


def build_pdf(title, profile, inputs, result, comparison_rows, reliability):
    buf=BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=16*mm,leftMargin=16*mm,topMargin=16*mm,bottomMargin=16*mm)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Small',parent=styles['BodyText'],fontSize=8.5,leading=11,textColor=colors.HexColor('#41566a')))
    styles.add(ParagraphStyle(name='HOrg',parent=styles['Title'],fontSize=21,leading=24,textColor=colors.HexColor('#0b1830')))
    story=[Paragraph(title,styles['HOrg']),Paragraph('HydrogenOrg technical research report',styles['Heading2']),Paragraph(f'Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}',styles['Small']),Spacer(1,8)]
    story += [Paragraph('Scientific position',styles['Heading2']),Paragraph('This report separates consolidated relations, engineering estimates, scenario models and research hypotheses. It does not certify industrial performance or material formation.',styles['BodyText']),Spacer(1,8)]
    key=[['Metric','Result'],['Water profile',profile],['Hydrogen output',f"{result['h2_kg_day']:.2f} kg/day"],['Specific electricity',f"{result['sec_kwh_kg']:.2f} kWh/kg H2"],['HHV efficiency',f"{result['hhv_eff_pct']:.2f} %"],['Recovered heat',f"{result['recovered_kwh_day']:.1f} kWh/day"],['Operational CO2 delta',f"{result['avoided_co2_kg_day']:.2f} kg/day"],['Salt recovery',f"{result['salt_kg_day']:.1f} kg/day"]]
    t=Table(key,colWidths=[65*mm,105*mm]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0b2234')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#cfdde6')),('VALIGN',(0,0),(-1,-1),'TOP'),('FONTSIZE',(0,0),(-1,-1),9),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f4f8fb')])]))
    story += [t,Spacer(1,10),Paragraph('Input parameters',styles['Heading2'])]
    data=[['Parameter','Value']]+[[k,str(v)] for k,v in inputs.items()]
    ti=Table(data,colWidths=[80*mm,90*mm],repeatRows=1); ti.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0b2234')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.25,colors.HexColor('#d4e0e8')),('FONTSIZE',(0,0),(-1,-1),7.5),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f6fafc')])]))
    story += [ti,PageBreak(),Paragraph('Model reliability',styles['Heading2'])]
    rel=[['Model element','Classification','Basis']]+[[k,v['level'],v['basis']] for k,v in reliability.items()]
    tr=Table(rel,colWidths=[55*mm,40*mm,75*mm],repeatRows=1); tr.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0b2234')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.25,colors.HexColor('#d4e0e8')),('FONTSIZE',(0,0),(-1,-1),7.5),('VALIGN',(0,0),(-1,-1),'TOP')]))
    story += [tr,Spacer(1,10),Paragraph('Core equations',styles['Heading2']),Paragraph('2 H2O -> 2 H2 + O2',styles['BodyText']),Paragraph('m_water = 9 x m_H2; m_O2 = 8 x m_H2',styles['BodyText']),Paragraph('Q_steam = m[c_p,liq(100-T0) + delta h_vap + c_p,steam(Tsteam-100)]',styles['BodyText']),Paragraph('SEC = E_net / m_H2; eta_HHV = HHV_H2 / SEC',styles['BodyText']),Spacer(1,8),Paragraph('Limitations',styles['Heading2']),Paragraph('Plasma kinetics, residence time, electrode or torch losses, gas separation performance, corrosion, chlorine chemistry, scale formation and carbon nanomaterial identity require experimental validation.',styles['BodyText'])]
    doc.build(story); return buf.getvalue()

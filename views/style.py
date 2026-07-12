import streamlit as st

def inject_style():
 st.markdown('''<style>
:root{--bg:#06111c;--panel:#0b1b2a;--line:rgba(255,255,255,.10);--text:#eef7fb;--muted:#91a7b7;--cyan:#19c7ff;--green:#62c945;--orange:#ff8a3d}
.stApp{background:radial-gradient(circle at 78% 0%,rgba(25,199,255,.10),transparent 25%),linear-gradient(180deg,#06111c 0%,#081725 100%);color:var(--text)}
.block-container{max-width:1580px;padding-top:2.6rem;padding-bottom:4rem}[data-testid="stSidebar"]{background:#06101a;border-right:1px solid var(--line)}[data-testid="stSidebar"] *{color:var(--text)}
h1,h2,h3,h4{color:var(--text)!important}p,li{color:var(--muted)}
.topbar{display:flex;justify-content:space-between;align-items:center;padding:14px 18px;border:1px solid var(--line);border-radius:14px;background:rgba(10,24,38,.92);margin-bottom:18px}.brand{font-weight:900;letter-spacing:1.3px}.brand span{color:var(--green)}.sys{color:var(--green);font-size:11px;font-weight:900;letter-spacing:1px}
.hero{display:grid;grid-template-columns:1.05fr .95fr;gap:26px;align-items:center;padding:34px;border:1px solid var(--line);border-radius:22px;background:linear-gradient(135deg,#0c2030,#123149);box-shadow:0 28px 75px rgba(0,0,0,.25)}.kicker{color:var(--green);font-size:12px;font-weight:900;letter-spacing:1.8px;text-transform:uppercase}.title{font-size:50px;line-height:1.03;font-weight:900;text-transform:uppercase;margin:12px 0}.title span{color:var(--cyan)}.lead{font-size:18px;line-height:1.65;color:var(--muted)}.hero-panel{padding:22px;border-radius:18px;background:#071421;border:1px solid var(--line)}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:20px 0}.metric{padding:20px;border:1px solid var(--line);border-radius:15px;background:#0b1b2a}.metric small{display:block;color:var(--muted);font-size:10px;font-weight:900;text-transform:uppercase}.metric strong{display:block;margin-top:10px;font-size:27px}.metric em{display:block;margin-top:7px;color:var(--cyan);font-size:11px;font-style:normal}.section{margin-top:22px;padding:24px;border:1px solid var(--line);border-radius:18px;background:rgba(11,27,42,.92)}
.reliability{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.rel{padding:15px;border:1px solid var(--line);border-radius:13px;background:#071421}.rel b{display:block;margin-bottom:6px}.pill{display:inline-flex;padding:5px 9px;border-radius:999px;font-size:10px;font-weight:900;text-transform:uppercase}
.eq{font-family:Consolas,monospace;padding:14px;border-radius:12px;background:#020b12;color:#d8edf8}.footer{margin-top:28px;padding:24px;border-radius:18px;background:#020b12;border:1px solid var(--line)}
div.stButton>button,div.stLinkButton>a,div.stDownloadButton>button{border-radius:8px!important;min-height:44px!important;font-weight:800!important}
@media(max-width:950px){.hero{grid-template-columns:1fr}.metrics,.reliability{grid-template-columns:1fr 1fr}}@media(max-width:620px){.metrics,.reliability{grid-template-columns:1fr}.title{font-size:34px}.topbar{flex-direction:column;align-items:flex-start}}
</style>''',unsafe_allow_html=True)

from __future__ import annotations
import streamlit as st
from .colors import PALETTE_OPTIONS, PALETTES

def _palette_values(name: str) -> dict:
    return PALETTES.get(name, PALETTES[PALETTE_OPTIONS[0]])

def apply_base_theme() -> None:
    css = """
    <style>
    :root { --bg: #ffffff; --bg2:#F3F5FA; --text:#262730; }
    .stApp, .block-container { background-color: var(--bg) !important; }
    .stSidebar { background-color: var(--bg2) !important; }
    .stMetric > div { font-size: 1.15rem; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def apply_palette_css(palette_name: str) -> None:
    p = _palette_values(palette_name)
    css = f"""
    <style>
      :root {{
        --title-from:{p['title_grad_from']};
        --title-to:{p['title_grad_to']};
        --card-from:{p['card_from']};
        --card-to:{p['card_to']};
        --accent:{p['accent']};
      }}
      .themed-title {{
        background: linear-gradient(90deg, var(--title-from), var(--title-to));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
      }}
      .filter-card {{
        border: 1px solid rgba(120,120,120,.2);
        background: linear-gradient(180deg, rgba(0,0,0,0.00), rgba(0,0,0,0.03));
        border-radius: 16px; padding: 14px 16px; margin: 6px 0 18px 0;
        box-shadow: 0 6px 16px rgba(0,0,0,.06);
      }}
      .kpi {{
        border-radius: 18px; padding: 18px 18px 14px 18px; color: white;
        background: linear-gradient(135deg, var(--card-from), var(--card-to));
        box-shadow: 0 10px 24px rgba(0,0,0,.12);
      }}
      .kpi .kpi-value {{ font-size: 1.8rem; font-weight: 800; line-height: 1; }}
      .kpi .kpi-label {{ opacity: .95; font-size: .95rem; }}

      /* Label dos widgets (texto acima do controle) */
      div[data-testid="stWidgetLabel"] p {{
        font-size: 28px !important;         
        font-weight: 800 !important;
        color: #333 !important;
        margin-bottom: 6px !important;
      }}

      div[data-baseweb="select"] > div {{
        min-height: 60px !important;         
        padding-top: 6px !important;
        padding-bottom: 6px !important;
      }}
      div[data-baseweb="select"] * {{
        font-size: 20px !important;         
      }}
      span[data-baseweb="tag"] {{
        transform: scale(1.05);          
      }}

      div[role="radiogroup"] label {{
        font-size: 26px !important;         
        font-weight: 700 !important;
        padding: 6px 10px !important;
        margin-right: 14px !important;
      }}

      .stTabs [role="tab"] {{
        font-size: 30px !important;          
        font-weight: 800 !important;
        padding: 8px 16px !important;
      }}
      .stTabs [role="tab"][aria-selected="true"] {{
        border-bottom: 6px solid currentColor !important;
      }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def color_sequence(palette_name: str) -> list[str]:
    return _palette_values(palette_name)["seq"]

# Principal.py
from __future__ import annotations
import os, sys, pathlib
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.theme import apply_base_theme, apply_palette_css, PALETTE_OPTIONS
from core.data import load_data
from ui_components.kpi_cards import render_kpis
from ui_components.filters import render_global_filters   # único filtro (Marca=arquivo; Categoria=canônica)
from ui_components.charts import chart_produtos_por_categoria, apply_filters

st.set_page_config(page_title="Análise Cuidados com a Pele", page_icon="🧴", layout="wide")

# Tema sempre claro + paleta
if "palette_name" not in st.session_state:
    st.session_state["palette_name"] = "Roxo & Rosa"

with st.sidebar:
    st.markdown("### Escolha a paleta de cores")
    st.session_state["palette_name"] = st.selectbox("Paleta de cores", options=PALETTE_OPTIONS)
    st.markdown("---")


apply_base_theme()  # tema claro fixo
apply_palette_css(st.session_state["palette_name"])

st.markdown(
    "<h1 class='themed-title' style='font-size:62px; line-height:1.1; margin:0;'>"
    "Dashboard Produtos de Cuidados com o Rosto"
    "</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<span style='font-size:28px; color:#363636; font-weight:500;'>Análise completa dos dados de produtos de cuidados com o rosto de diferentes marcas brasileiras.</span>",
    unsafe_allow_html=True
)

# Marca d'água
st.markdown("""
<style>
  .watermark { position: fixed; top: 8px; right: 16px; opacity: .25; font-size: 12px; pointer-events: none; z-index: 9999; }
</style>
<div class="watermark">Ana Laura - Ciência de Dados</div>
""", unsafe_allow_html=True)

# ====== DADOS ======
df = load_data()

# ====== KPIs GLOBAIS (sem filtro) ======
render_kpis(df)
st.markdown("---")

# ====== ÚNICO BLOCO DE FILTROS (para o gráfico) ======
st.markdown("<span style='font-size:28px; font-weight:600;'>Opções do gráfico</span>", unsafe_allow_html=True)

# Marca = arquivos (_source_file) | Categoria = lista canônica
sel_files, sel_cats = render_global_filters(df)

# Aplica filtros UMA vez (por arquivo + categoria)
df_chart = apply_filters(df, marcas=None, cats=sel_cats, source_files=sel_files)

# ====== GRÁFICO ======
chart_produtos_por_categoria(
    df_chart,
    st.session_state['palette_name'],
    key_prefix='cat',
    legend_size=16  # legenda maior
)

st.markdown("---")

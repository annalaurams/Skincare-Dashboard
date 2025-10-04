from __future__ import annotations
import sys, pathlib
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.theme import apply_base_theme, apply_palette_css, PALETTE_OPTIONS
from core.data import load_data
from ui_components.kpi_cards import render_kpis
from ui_components.filters import render_global_filters  
from ui_components.charts import chart_produtos_por_categoria, apply_filters

st.set_page_config(page_title="Análise Cuidados com a Pele", page_icon="🧴", layout="wide")

with st.sidebar:
    st.markdown(
        '<p style="font-size:22px; font-weight:bold; ">Escolha a paleta de cores</p>',
        unsafe_allow_html=True
    )
    st.session_state["palette_name"] = st.selectbox("Paleta de cores", options=PALETTE_OPTIONS)
    st.markdown("---")


apply_base_theme()
apply_palette_css(st.session_state["palette_name"])

st.markdown(
    "<h1 class='themed-title' style='font-size:62px; line-height:1.1; margin:0;'>Dashboard Produtos de Cuidados com o Rosto</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<span style='font-size:28px; color:#363636; font-weight:500;'>Análise completa dos dados de produtos de cuidados com o rosto de diferentes marcas brasileiras.</span>",
    unsafe_allow_html=True
)

st.markdown("""
<style>
.section-title   { font-size: 34px; font-weight: 700; color:#262730; margin-top: 28px; }
.section-sub     { font-size: 26px; font-weight: 600; color:#363636; margin: 18px 0 8px; }
.filter-label    { font-size: 22px; font-weight: 600; color:#363636; display:block; margin: 12px 0 6px; }


div[role="radiogroup"] label {
    font-size: 42px   
    color: #262730 
    font-weight: 700 
    padding: 6px 0 
}
div[role="radiogroup"] input[type="radio"] {
    width: 22px      
    height: 22px 
    margin-right: 10px 
}

.stTabs [role="tab"] {
    font-size: 22px   
    padding: 12px 24px 
    font-weight: 600 
}
.stTabs [role="tab"][aria-selected="true"] {
    color: #7f00b2   
}
</style>
""", unsafe_allow_html=True)

df = load_data()

render_kpis(df)
st.markdown("---")

st.markdown("<div class='section-title'>Produtos por Marca e Categoria</div>", unsafe_allow_html=True)
st.markdown("<div class='section-sub'>Aplicar Filtros</div>", unsafe_allow_html=True)

# Marca (multi), Categoria (única) e Ordenação (3 opções)
sel_files, sel_cats, order_option = render_global_filters(df)

df_chart = apply_filters(df, marcas=None, cats=sel_cats, source_files=sel_files)

# GRÁFICO 
chart_produtos_por_categoria(
    df_chart,
    st.session_state['palette_name'],
    key_prefix='cat',
    legend_size=24,
    selected_files=sel_files,
    hover_box="right",
    order_option=order_option,      
    show_internal_title=False       
)

st.markdown("---")

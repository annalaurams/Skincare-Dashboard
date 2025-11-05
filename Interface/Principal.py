import streamlit as st
from include import *  
from ui_components.kpi_cards import render_kpis
from ui_components.filters import (
    render_filters_por_categoria,
    render_filters_por_marca,
)
from ui_components.charts import (
    apply_filters,
    chart_produtos_por_categoria,
    chart_categorias_por_marca,
)

st.set_page_config(page_title="Análise Cuidados com a Pele", page_icon="🧴", layout="wide")

if "palette_name" not in st.session_state:
    st.session_state["palette_name"] = "Solaris"

SEQ = color_sequence(st.session_state["palette_name"]) or ["#6e56cf", "#22c55e", "#eab308", "#ef4444"]
ACCENT_COLOR = SEQ[0] if SEQ else "#6e56cf"
ACCENT_COLOR_2 = SEQ[1] if len(SEQ) > 1 else "#22c55e"
st.markdown("""
<style>
:root{
  --brand: var(--accent, var(--primary, var(--color-accent, #7f00b2)));
  --brand-strong: var(--accent-strong, var(--primary-strong, #5e0090));
  --brand-weak: var(--accent-weak, var(--primary-weak, #efe7fb));
  --surface-soft: var(--surface-soft, #fbfbfe);
  --surface-softer: var(--surface-softer, #ffffff);
  --text: var(--text, #2e2e2e);
  --text-strong: var(--text-strong, #1a1a1a);
  --ring: var(--ring, rgba(0,0,0,.08));
}

details.expander-btn > summary{
  width:100%;
  cursor:pointer;
  list-style:none;
  padding:20px 28px;
  margin:32px 0 16px;
  background:linear-gradient(135deg,var(--surface-soft) 0%,var(--surface-softer) 100%);
  border:3px solid var(--brand);
  border-radius:18px;
  box-shadow:0 4px 16px var(--ring);
  font-size:26px;
  font-weight:800;
  color:var(--brand-strong);
  transition:all .25s ease;
  display:flex; align-items:center; gap:12px;
}
details.expander-btn > summary:hover{ transform:translateY(-2px); box-shadow:0 6px 20px var(--ring); }
details.expander-btn[open] > summary{
  border-bottom-left-radius:0; border-bottom-right-radius:0;
  background:var(--brand); color:#fff;
}
details.expander-btn > summary::-webkit-details-marker{ display:none; }

details.expander-btn .expander-body{
  padding:28px 32px;
  background:linear-gradient(180deg,var(--surface-soft) 0%,var(--surface-softer) 100%);
  border:3px solid var(--brand); border-top:none;
  border-bottom-left-radius:18px; border-bottom-right-radius:18px;
  box-shadow:0 6px 20px var(--ring);
}

/* Texto maior */
.note-icon{ font-size:32px; margin-right:8px; display:inline-block; }
.note-text{ font-size:21px; line-height:1.9; color:var(--text); text-align:justify; }
.note-text strong{ color:var(--text-strong); font-weight:800; }

/* Separador */
.note-divider{ height:2px; margin:20px 0; border-radius:2px;
  background:linear-gradient(90deg,transparent 0%,var(--brand) 50%,transparent 100%); }

/* Marcas (links) */
.brand-list{ display:inline-flex; flex-wrap:wrap; gap:10px; margin:6px 0 2px; }
.brand-link{
  display:inline-block; padding:6px 14px; border-radius:20px; font-size:17px; font-weight:700;
  text-decoration:none; color:var(--brand-strong); background:var(--brand-weak);
  border:1px solid var(--brand); transition:transform .15s ease, box-shadow .15s ease;
}
.brand-link:hover{ transform:translateY(-1px); box-shadow:0 2px 8px var(--ring); }

/* Botão GitHub */
.repo-button{
  display:inline-block; background:var(--brand); color:#fff !important; text-decoration:none;
  font-weight:700; padding:14px 28px; border-radius:12px; margin-top:22px; font-size:18px;
  transition:transform .2s ease, filter .2s ease; border:none;
}
.repo-button:hover{ transform:translateY(-2px); filter:brightness(0.95); }
</style>
""", unsafe_allow_html=True)

st.markdown(
"""
<details class="expander-btn">
<summary>Mais informações sobre os dados</summary>
<div class="expander-body">
<div class="note-text">
<span class="note-icon">💡</span><strong>Nota:</strong> Os dados apresentados neste dashboard foram coletados por meio dos sites oficiais de cada marca brasileira abordada, utilizando técnicas de <em>web scraping</em> desenvolvidas em <strong>Python</strong>.
<br><br>

<strong>Marcas incluídas (sites oficiais):</strong>
<div class="brand-list">
<a class="brand-link" href="https://www.beyoung.com.br/" target="_blank" rel="nofollow noopener">Beyoung</a>
<a class="brand-link" href="https://www.creamy.com.br/" target="_blank" rel="nofollow noopener">Creamy</a>
<a class="brand-link" href="https://www.oceane.com.br/" target="_blank" rel="nofollow noopener">Oceane</a>
<a class="brand-link" href="https://meuollie.com.br/" target="_blank" rel="nofollow noopener">Ollie</a>
<a class="brand-link" href="https://www.sallve.com.br/" target="_blank" rel="nofollow noopener">Sallve</a>
</div>

<div class="note-divider"></div>

<strong>Complementos manuais:</strong> alguns valores foram ajustados manualmente com base nas informações disponíveis nas bases oficiais das marcas.
<br>
<strong>Período de coleta:</strong>  Este dashboard reflete o estado dos produtos até essa data -> outubro de 2025.
<br>
<strong>Escopo considerado:</strong> não incluímos itens promocionais e nem combos, <em>apenas produtos individuais</em>.
<br>
<strong>Limpeza e padronização:</strong> as variáveis analisadas (tipos de pele, benefícios, ingredientes ativos, preço, quantidade e categorias) foram normalizadas para permitir comparações entre marcas e características.
<center>
<a href="https://github.com/annalaurams" target="_blank" class="repo-button">Código neste repositório no GitHub</a>
</center>
</div>
</div>
</details>
""",
unsafe_allow_html=True
)

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
    font-size: 28px !important;  
    color: #262730 !important;
    font-weight: 700 !important;
    padding: 6px 0 !important;
}
div[role="radiogroup"] input[type="radio"] {
    width: 22px !important;     
    height: 22px !important;
    margin-right: 10px !important;
}

.stTabs [role="tab"] {
    font-size: 22px;   
    padding: 12px 24px;
    font-weight: 600;
}
.stTabs [role="tab"][aria-selected="true"] {
    color: #7f00b2;
}

.mode-description {
    font-size: 18px;
    color: #555;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# Carrega dados das marcas (CSV)
df = load_data()

render_kpis(df)
st.markdown("---")

st.markdown("<div class='section-title'>Análise de Produtos</div>", unsafe_allow_html=True)

modo_tabs = st.tabs(["Fixar Uma Categoria", "Fixar uma Marca"])

# MODO 1: POR CATEGORIA (1 categoria, múltiplas marcas)
with modo_tabs[0]:
    st.markdown(
        "<div class='mode-description'> <b>Neste modo:</b> Selecione apenas uma categoria e escolha quais marcas deseja visualizar a quantidade de produtos na categoria escolhida.</div>",
        unsafe_allow_html=True
    )
    st.markdown("<div class='section-sub'>Aplicar Filtros Para Gerar o Gráfico</div>", unsafe_allow_html=True)
    
    sel_files, sel_cats, order_option = render_filters_por_categoria(df)
    df_chart = apply_filters(df, marcas=None, cats=sel_cats, source_files=sel_files)
    
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

# MODO 2: POR MARCA (1 marca, TODAS as categorias)
with modo_tabs[1]:
    st.markdown(
        "<div class='mode-description'><b>Neste modo:</b> Selecione apenas uma marca e veja a quantidade de produtos em cada categoria que ela possui.</div>",
        unsafe_allow_html=True
    )
    st.markdown("<div class='section-sub'>Aplicar Filtros</div>", unsafe_allow_html=True)
    
    sel_marca, order_option_marca = render_filters_por_marca(df)
    df_chart_marca = apply_filters(df, marcas=None, cats=None, source_files=[sel_marca] if sel_marca else [])
    
    chart_categorias_por_marca(
        df_chart_marca,
        st.session_state['palette_name'],
        key_prefix='marca',
        legend_size=24,
        order_option=order_option_marca,
        show_internal_title=False
    )

st.markdown("---")
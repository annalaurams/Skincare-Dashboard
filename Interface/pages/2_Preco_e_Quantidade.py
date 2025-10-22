from __future__ import annotations
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path
import sys

from core.theme import apply_base_theme, apply_palette_css, color_sequence
from core.data import load_data

sys.path.append("/home/usuario/Área de trabalho/Dados/models")
try:
    from category import CATEGORY_CANONICAL_ORDER  
except Exception:
    CATEGORY_CANONICAL_ORDER = []

if "palette_name" not in st.session_state:
    st.session_state["palette_name"] = "Solaris"  

st.set_page_config(page_title="Skincare • Preço & Quantidade", page_icon="📊", layout="wide")

TITLE_TEXT          = "Preço & Quantidade"
TAGLINE_TEXT        = "Compare os valores, identifique o melhor custo por unidade e veja a relação preço × quantidade."
TITLE_SIZE          = 60
TAGLINE_SIZE        = 26
SECTION_TITLE_SIZE  = 32
AXIS_TITLE_SIZE     = 24
AXIS_TICK_SIZE      = 24
LEGEND_FONT_SIZE    = 34
SCATTER_MARKER_SIZE = 18
CHART_HEIGHT        = 750

KPI_CARD_HEIGHT     = 180
KPI_BORDER_PX       = 5

KPI_TITLE_SIZE      = 30
KPI_VALUE_SIZE      = 10
KPI_HELP_SIZE       = 20

apply_base_theme() 
apply_palette_css(st.session_state["palette_name"])
SEQ = color_sequence(st.session_state["palette_name"])

def accent(i: int = 0) -> str: return SEQ[i % len(SEQ)] if SEQ else "#6e56cf"
def text_color() -> str:       return "#262730"
def subtext_color() -> str:    return "#555"
def panel_bg() -> str:         return "#ffffff"

def _pretty_from_source(fname: str) -> str:
    stem = Path(fname).stem
    for suf in ["_products", "_skincare", "_cosmetics", "_dados"]:
        stem = stem.replace(suf, "")
    return stem.replace("_", " ").title()

def brl(x: float | int | None) -> str:
    if x is None or pd.isna(x): return "—"
    return f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def most_common_unit(df: pd.DataFrame) -> str | None:
    s = df["quantidade_unidade"].dropna()
    return s.value_counts().idxmax() if not s.empty else None

def fmt_qtd(val, unit) -> str:
    if pd.isna(val): return "—"
    if pd.isna(unit) or unit is None:
        try:
            return f"{float(val):.2f}"
        except Exception:
            return str(val)
    try:
        if float(val).is_integer():
            return f"{int(val)} {unit}"
    except Exception:
        pass
    return f"{float(val):.2f} {unit}"

def style_axes(fig, height: int = CHART_HEIGHT):
    fig.update_layout(
        font=dict(color=text_color()),
        xaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE, color=text_color()),
                   tickfont=dict(size=AXIS_TICK_SIZE, color=text_color())),
        yaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE, color=text_color()),
                   tickfont=dict(size=AXIS_TICK_SIZE, color=text_color())),
        height=height,
        paper_bgcolor=panel_bg(),
        plot_bgcolor=panel_bg(),
        title_font_color=text_color(),
        margin=dict(t=70, b=70, l=20, r=20),
    )
    return fig

# =======================
# Conversão g ↔ mL (densidade estimada por categoria)
# =======================
DENSIDADE_PADRAO = {
    "sérum": 0.95, "serum": 0.95,
    "hidratante": 1.05,
    "creme": 1.10,
    "manteiga": 1.15,
    "óleo": 0.90, "oleo": 0.90,
    "_default": 1.00
}

def _match_density_key(texto: str) -> float:
    t = (texto or "").lower()
    for k, v in DENSIDADE_PADRAO.items():
        if k == "_default":
            continue
        if k in t:
            return v
    return DENSIDADE_PADRAO["_default"]

def get_densidade(row):
    # usa a categoria como heurística
    return _match_density_key(str(row.get("categoria", "")))

def to_grams(valor, unidade, densidade):
    if pd.isna(valor):
        return np.nan
    u = (str(unidade) if unidade is not None else "").strip().lower()
    if u in ["g", "grama", "gramas"]:
        return float(valor)
    if u in ["ml", "ml", "mililitro", "mililitros"]:
        return float(valor) * float(densidade or 1.0)
    return np.nan

def to_milliliters(valor, unidade, densidade):
    if pd.isna(valor):
        return np.nan
    u = (str(unidade) if unidade is not None else "").strip().lower()
    if u in ["ml", "ml", "mililitro", "mililitros"]:
        return float(valor)
    if u in ["g", "grama", "gramas"]:
        d = float(densidade or 0.0)
        return float(valor) / d if d > 0 else np.nan
    return np.nan

# =======================
# Carregamento de dados
# =======================
df = load_data()  

# Adiciona estimativa de densidade e colunas convertidas
if not df.empty:
    df["densidade_est"] = df.apply(get_densidade, axis=1)
    df["qtd_g"]  = df.apply(lambda r: to_grams(r.get("quantidade_valor"), r.get("quantidade_unidade"), r.get("densidade_est")), axis=1)
    df["qtd_ml"] = df.apply(lambda r: to_milliliters(r.get("quantidade_valor"), r.get("quantidade_unidade"), r.get("densidade_est")), axis=1)

# Preparação de listas (mesma lógica da tela principal)
uses_files = "_source_file" in df.columns and df["_source_file"].notna().any()

if uses_files:
    files = sorted(df["_source_file"].dropna().unique().tolist())
    LABEL_MAP = { _pretty_from_source(f): f for f in files }  
    BRAND_LABELS = list(LABEL_MAP.keys())  
else:
    brands_col = sorted(df["marca"].dropna().unique().tolist()) if "marca" in df.columns else []
    LABEL_MAP = { b: b for b in brands_col } 
    BRAND_LABELS = list(LABEL_MAP.keys())

CAT_OPTS = CATEGORY_CANONICAL_ORDER[:] if CATEGORY_CANONICAL_ORDER else sorted(df["categoria"].dropna().unique().tolist())

# Título + Tagline
st.markdown(
    f"<h1 style='margin:0;color:{accent(0)};font-size:{TITLE_SIZE}px'>{TITLE_TEXT}</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<div style='margin:.25rem 0 1rem 0; color:{subtext_color()}; font-size:{TAGLINE_SIZE}px'>{TAGLINE_TEXT}</div>",
    unsafe_allow_html=True,
)

# FILTROS (OBRIGATÓRIOS) — KPIs
st.markdown(f"<h3 style='font-size:32px;margin:.75rem 0 .5rem 0;'>Filtros</h3>", unsafe_allow_html=True)

# Marca 
sel_brand_label_kpi = st.selectbox("Marca (KPIs / Ofertas)", options=BRAND_LABELS, index=0)
sel_brand_value_kpi = LABEL_MAP[sel_brand_label_kpi]

if uses_files:
    df_brand_for_default = df[df["_source_file"] == sel_brand_value_kpi]
else:
    df_brand_for_default = df[df["marca"] == sel_brand_value_kpi]
present_cats_for_brand = [c for c in CAT_OPTS if c in df_brand_for_default["categoria"].dropna().unique().tolist()]
default_cat_for_brand = present_cats_for_brand[0] if present_cats_for_brand else (CAT_OPTS[0] if CAT_OPTS else None)
default_cat_index = CAT_OPTS.index(default_cat_for_brand) if (default_cat_for_brand in CAT_OPTS) else 0

sel_cat_kpi = st.selectbox("Categoria (KPIs / Ofertas)", options=CAT_OPTS, index=default_cat_index)

if uses_files:
    df_kpi = df[(df["_source_file"] == sel_brand_value_kpi) & (df["categoria"] == sel_cat_kpi)].copy()
else:
    df_kpi = df[(df["marca"] == sel_brand_value_kpi) & (df["categoria"] == sel_cat_kpi)].copy()

#  preço médio, quantidade média, melhor custo
def kpi_box(title: str, value: str, help_text: str = "", color_idx: int = 0, custom_value_size: int = None):
    value_size = custom_value_size if custom_value_size is not None else KPI_VALUE_SIZE
    st.markdown(
        f"""
        <div style="
            border:{KPI_BORDER_PX}px solid {accent(color_idx)};
            border-radius:30px; padding:30px 30px; background:{panel_bg()};
            display:flex; flex-direction:column; gap:.3rem; width:700px;  height:{KPI_CARD_HEIGHT}px;">
          <span style="font-size:{KPI_TITLE_SIZE}px; color:{subtext_color()};">{title}</span>
          <div style="font-weight:800; font-size:{value_size}px; color:{text_color()}; line-height:1;">
            {value}
          </div>
          <span style="font-size:{KPI_HELP_SIZE}px; color:{subtext_color()};">{help_text}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

c1, c2, c3 = st.columns(3)

if df_kpi.empty:
    with c1: kpi_box("Preço Médio", "—", custom_value_size=60)
    with c2: kpi_box("Quantidade Médio", "—", help_text="—", color_idx=1, custom_value_size=50)
    with c3: kpi_box("Melhor custo/unid", "—", help_text="—", color_idx=2, custom_value_size=45)
else:
    preco_med = df_kpi["preco"].mean()
    qtd_med   = df_kpi["quantidade_valor"].dropna().mean()

    df_cost = df_kpi.dropna(subset=["quantidade_valor"]).copy()
    unit = most_common_unit(df_cost)
    if unit is not None:
        df_cost = df_cost[df_cost["quantidade_unidade"] == unit].copy()
        if not df_cost.empty:
            df_cost["custo_por_unid"] = df_cost["preco"] / df_cost["quantidade_valor"]
    if df_cost.empty:
        best_cost, best_name = None, "—"
    else:
        idx = df_cost["custo_por_unid"].idxmin()
        best_cost, best_name = df_cost.loc[idx, "custo_por_unid"], df_cost.loc[idx, "nome"]

    with c1:
        kpi_box("Preço Médio", brl(preco_med), custom_value_size=30)
    with c2:
        kpi_box("Quantidade Média",
                f"{qtd_med:.2f}" if pd.notna(qtd_med) else "—",
                help_text=f"Unidade: {unit or '—'}",
                color_idx=1, custom_value_size=30)
    with c3:
        kpi_box(f"Melhor custo/{unit or '—'}", brl(best_cost),
                help_text=best_name, color_idx=2, custom_value_size=30)

# ======================= GRÁFICO — Dispersão (com seletor de unidade g/mL) =======================
st.markdown(f"<h3 style='font-size:{SECTION_TITLE_SIZE}px;margin:1.25rem 0 .25rem 0;'>Relação Preço × Quantidade</h3>", unsafe_allow_html=True)

# Marca 
brand_scatter_label = st.selectbox(
    "Marca (Dispersão)",
    options=BRAND_LABELS,
    index=BRAND_LABELS.index(sel_brand_label_kpi) if sel_brand_label_kpi in BRAND_LABELS else 0
)
brand_scatter_value = LABEL_MAP[brand_scatter_label]

# Categorias 
if uses_files:
    df_brand_sc = df[df["_source_file"] == brand_scatter_value].copy()
else:
    df_brand_sc = df[df["marca"] == brand_scatter_value].copy()

present_cats_scatter = [c for c in CAT_OPTS if c in df_brand_sc["categoria"].dropna().unique().tolist()]
default_scatter_cats = present_cats_scatter if present_cats_scatter else CAT_OPTS

sel_cats_scatter = st.multiselect(
    "Categoria (Dispersão) — múltiplas",
    options=CAT_OPTS,
    default=default_scatter_cats
)

# Seletor de unidade para o eixo X (quantidade)
unidade_plot = st.radio("Unidade para visualização", ["g", "mL"], horizontal=True)

if uses_files:
    df_sc = df[(df["_source_file"] == brand_scatter_value)].copy()
else:
    df_sc = df[(df["marca"] == brand_scatter_value)].copy()

if sel_cats_scatter:
    df_sc = df_sc[df_sc["categoria"].isin(sel_cats_scatter)]

# Seleciona a coluna de quantidade convertida conforme a unidade escolhida
col_qtd = "qtd_g" if unidade_plot == "g" else "qtd_ml"

# Mantém todos os itens; exige ter a quantidade convertida selecionada
df_sc = df_sc.dropna(subset=[col_qtd, "preco"]).copy()

if df_sc.empty:
    st.info("Sem dados suficientes para exibir a dispersão.")
else:
    df_sc["preco_fmt"] = df_sc["preco"].map(brl)
    df_sc["qtd_fmt_origem"] = [fmt_qtd(v, u) for v, u in zip(df_sc.get("quantidade_valor"), df_sc.get("quantidade_unidade"))]
    # formata a quantidade na unidade escolhida
    df_sc["qtd_plot"] = df_sc[col_qtd].astype(float)
    df_sc["qtd_plot_fmt"] = df_sc["qtd_plot"].map(lambda x: f"{x:.2f} {unidade_plot}" if pd.notna(x) else "—")

    customdata_sc = df_sc[["nome", "preco_fmt", "qtd_fmt_origem", "qtd_plot_fmt", "categoria"]].values

    fig_sc = px.scatter(
        df_sc,
        x="qtd_plot",
        y="preco",
        color="categoria",
        color_discrete_sequence=SEQ,
        labels={
            "qtd_plot": f"Quantidade ({unidade_plot})", 
            "preco": "Preço (R$)"
        },
        title=f"Preço vs. Quantidade — {brand_scatter_label}",
        hover_data={}
    )
    fig_sc.update_traces(
        marker=dict(size=SCATTER_MARKER_SIZE, line=dict(width=0)),
        customdata=customdata_sc,
        hovertemplate="<b>%{customdata[0]}</b><br>Preço: %{customdata[1]}<br>Qtd (origem): %{customdata[2]}<br>Qtd (plot): %{customdata[3]}<br>Categoria: %{customdata[4]}<extra></extra>"
    )
    fig_sc.update_layout(
        showlegend=True,
        title_font_size=32,
        title_font_color=text_color(),
        legend=dict(font=dict(size=LEGEND_FONT_SIZE, color=text_color())),
        hoverlabel=dict(font_size=28, font_color="gray")
    )
    style_axes(fig_sc, height=CHART_HEIGHT)
    st.plotly_chart(fig_sc, use_container_width=True)

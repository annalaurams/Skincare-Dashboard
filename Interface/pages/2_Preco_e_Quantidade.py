# Preco_Quantidade.py
from __future__ import annotations
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

from core.theme import apply_base_theme, apply_palette_css, color_sequence
from core.data import load_data

st.set_page_config(page_title="Skincare • Preço & Quantidade", page_icon="📊", layout="wide")

# =========================
# APARÊNCIA (edite aqui)
# =========================
TITLE_TEXT          = "Preço & Quantidade"
TAGLINE_TEXT        = "Compare preços, identifique o melhor custo por unidade e veja a relação preço × quantidade."
TITLE_SIZE          = 30     # h1
TAGLINE_SIZE        = 16     # subtítulo
SECTION_TITLE_SIZE  = 22     # títulos de seção
AXIS_TITLE_SIZE     = 18
AXIS_TICK_SIZE      = 14
LEGEND_FONT_SIZE    = 16
SCATTER_MARKER_SIZE = 14     # bolinhas do scatter
CHART_HEIGHT        = 560

# KPI cards (tamanho/estética)
KPI_CARD_HEIGHT     = 110
KPI_BORDER_PX       = 3

# =========================
# Tema claro + paleta (persistente)
# =========================
if "palette_name" not in st.session_state:
    st.session_state["palette_name"] = "Roxo & Rosa"

apply_base_theme()  # claro fixo
apply_palette_css(st.session_state["palette_name"])
SEQ = color_sequence(st.session_state["palette_name"])

def accent(i: int = 0) -> str: return SEQ[i % len(SEQ)] if SEQ else "#6e56cf"
def text_color() -> str:       return "#262730"
def subtext_color() -> str:    return "#555"
def panel_bg() -> str:         return "#ffffff"

# =========================
# Helpers
# =========================
def brl(x: float | int | None) -> str:
    if x is None or pd.isna(x): return "—"
    return f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def most_common_unit(df: pd.DataFrame) -> str | None:
    s = df["quantidade_unidade"].dropna()
    return s.value_counts().idxmax() if not s.empty else None

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

# =========================
# Dados
# =========================
df = load_data()  # carrega todos CSVs (com _source_file, preco float, quantidade_valor/unidade, etc.)

# =========================
# Título + Tagline
# =========================
st.markdown(
    f"<h1 style='margin:0;color:{accent(0)};font-size:{TITLE_SIZE}px'>{TITLE_TEXT}</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<div style='margin:.25rem 0 1rem 0; color:{subtext_color()}; font-size:{TAGLINE_SIZE}px'>{TAGLINE_TEXT}</div>",
    unsafe_allow_html=True,
)

# =======================================================
# FILTROS (UMA VEZ) — KPIs e “Melhores ofertas”
#   • marca: 1 (obrigatório)
#   • categoria: 1 (obrigatório)
# =======================================================
st.markdown(f"<h3 style='font-size:{SECTION_TITLE_SIZE}px;margin:.75rem 0 .5rem 0;'>Filtros</h3>", unsafe_allow_html=True)
brands = sorted(df["marca"].dropna().unique().tolist())
cats   = sorted(df["categoria"].dropna().unique().tolist())

fc1, fc2 = st.columns(2)
with fc1:
    sel_brand_kpi = st.selectbox("Marca (KPIs / Ofertas)", options=brands, index=0)
with fc2:
    sel_cat_kpi   = st.selectbox("Categoria (KPIs / Ofertas)", options=cats, index=0)

df_kpi = df[(df["marca"] == sel_brand_kpi) & (df["categoria"] == sel_cat_kpi)].copy()

# =========================
# KPIs (3) – preço médio, quantidade média, melhor custo
# =========================
def kpi_box(title: str, value: str, help_text: str = "", color_idx: int = 0):
    st.markdown(
        f"""
        <div style="
            border:{KPI_BORDER_PX}px solid {accent(color_idx)};
            border-radius:14px; padding:12px 14px; background:{panel_bg()};
            display:flex; flex-direction:column; gap:.3rem; height:{KPI_CARD_HEIGHT}px;">
          <span style="font-size:{TAGLINE_SIZE-2}px; color:{subtext_color()};">{title}</span>
          <div style="font-weight:800; font-size:{TITLE_SIZE-8}px; color:{text_color()}; line-height:1;">
            {value}
          </div>
          <span style="font-size:{TAGLINE_SIZE-3}px; color:{subtext_color()};">{help_text}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

c1, c2, c3 = st.columns(3)
if df_kpi.empty:
    with c1: kpi_box("Preço Médio", "—")
    with c2: kpi_box("Quantidade Média", "—", help_text="—", color_idx=1)
    with c3: kpi_box("Melhor custo/unid", "—", help_text="—", color_idx=2)
else:
    preco_med = df_kpi["preco"].mean()
    qtd_med   = df_kpi["quantidade_valor"].dropna().mean()
    # melhor custo/unidade
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

    with c1: kpi_box("Preço Médio", brl(preco_med))
    with c2: kpi_box("Quantidade Média", f"{qtd_med:.2f}" if pd.notna(qtd_med) else "—",
                     help_text=f"Unidade: {unit or '—'}", color_idx=1)
    with c3: kpi_box(f"Melhor custo/{unit or '—'}", brl(best_cost), help_text=best_name, color_idx=2)

# =========================
# Top 3 Melhores Ofertas (usa o mesmo filtro dos KPIs)
# =========================
st.markdown(f"<h3 style='font-size:{SECTION_TITLE_SIZE}px;margin:1rem 0 .25rem 0;'>⚡ Melhores Ofertas</h3>", unsafe_allow_html=True)
if df_kpi.empty:
    st.caption("Sem itens nessa marca+categoria.")
else:
    df_cost2 = df_kpi.dropna(subset=["quantidade_valor"]).copy()
    unit2 = most_common_unit(df_cost2)
    if unit2 is not None:
        df_cost2 = df_cost2[df_cost2["quantidade_unidade"] == unit2].copy()
        if not df_cost2.empty:
            df_cost2["custo_por_unid"] = df_cost2["preco"] / df_cost2["quantidade_valor"]
    top = (
        df_cost2.sort_values("custo_por_unid", ascending=True)
                .head(3)[["nome","marca","categoria","quantidade","preco","custo_por_unid"]]
        if not df_cost2.empty else pd.DataFrame()
    )
    cols = st.columns(3)
    if top.empty:
        st.caption("Sem base suficiente para calcular custo por unidade.")
    else:
        for i, (_, r) in enumerate(top.iterrows()):
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="
                        border:{KPI_BORDER_PX}px solid {accent(i)};
                        border-radius:14px; padding:12px 14px; margin-bottom:10px;
                        background:{panel_bg()}; height:{KPI_CARD_HEIGHT+40}px;">
                      <div style="font-weight:700; color:{text_color()}; font-size:{TAGLINE_SIZE}px;">{r['nome']}</div>
                      <div style="font-size:{TAGLINE_SIZE-4}px; color:{subtext_color()}; margin-top:2px;">
                        {r['marca']} • {r['categoria']} • {r['quantidade']}
                      </div>
                      <div style="margin-top:6px; font-weight:800; color:{accent(i)}; font-size:{TAGLINE_SIZE}px;">
                        {brl(r['custo_por_unid'])}/{unit2 or 'unid'} — {brl(r['preco'])}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# =======================================================
# GRÁFICO 1 — Dispersão (1 marca obrigatória)
# =======================================================
st.markdown(f"<h3 style='font-size:{SECTION_TITLE_SIZE}px;margin:1.25rem 0 .25rem 0;'>Relação Preço × Quantidade</h3>", unsafe_allow_html=True)
brand_scatter = st.selectbox("Marca (Dispersão)", options=brands, index=brands.index(sel_brand_kpi) if sel_brand_kpi in brands else 0)
df_sc = df[df["marca"] == brand_scatter].dropna(subset=["quantidade_valor"]).copy()
unit_sc = most_common_unit(df_sc)
if unit_sc is not None:
    df_sc = df_sc[df_sc["quantidade_unidade"] == unit_sc]

if df_sc.empty:
    st.info("Sem dados suficientes para exibir a dispersão.")
else:
    fig_sc = px.scatter(
        df_sc,
        x="quantidade_valor", y="preco",
        color="categoria", color_discrete_sequence=SEQ,
        hover_data={"nome": True, "categoria": True, "quantidade": True, "preco": ':.2f'},
        labels={"quantidade_valor": f"Quantidade ({unit_sc})" if unit_sc else "Quantidade", "preco": "Preço (R$)"},
        title=f"Preço vs. Quantidade — {brand_scatter}"
    )
    fig_sc.update_traces(marker=dict(size=SCATTER_MARKER_SIZE, line=dict(width=0)))
    fig_sc.update_layout(showlegend=True,
                         legend=dict(font=dict(size=LEGEND_FONT_SIZE, color=text_color())))
    style_axes(fig_sc, height=CHART_HEIGHT)
    st.plotly_chart(fig_sc, use_container_width=True)

# =======================================================
# GRÁFICO 2 — Preço médio por Categoria (1 marca) + seleção de categorias
# =======================================================
st.markdown(f"<h3 style='font-size:{SECTION_TITLE_SIZE}px;margin:1rem 0 .25rem 0;'>Preço médio por Categoria (por marca)</h3>", unsafe_allow_html=True)
brand_bycat = st.selectbox("Marca (Preço por Categoria)", options=brands, index=brands.index(sel_brand_kpi) if sel_brand_kpi in brands else 0)
df_bc_all = df[df["marca"] == brand_bycat].copy()
cats_brand = sorted(df_bc_all["categoria"].dropna().unique().tolist())
sel_cats_bc = st.multiselect("Categorias a exibir", options=cats_brand, default=cats_brand)

df_bc = df_bc_all[df_bc_all["categoria"].isin(sel_cats_bc)]
if df_bc.empty:
    st.info("Sem dados para os filtros atuais.")
else:
    by_cat = df_bc.groupby("categoria", as_index=False)["preco"].mean().rename(columns={"preco":"preco_medio"})
    fig_bcat = px.bar(
        by_cat.sort_values("preco_medio", ascending=False),
        x="categoria", y="preco_medio",
        color="categoria", color_discrete_sequence=SEQ,
        labels={"categoria":"Categoria", "preco_medio":"Preço médio (R$)"},
        title=f"Preço médio por Categoria — {brand_bycat}"
    )
    fig_bcat.update_traces(texttemplate="%{y:.2f}", textposition="outside")
    fig_bcat.update_layout(showlegend=False, xaxis_tickangle=-20,
                           legend=dict(font=dict(size=LEGEND_FONT_SIZE, color=text_color())))
    style_axes(fig_bcat, height=CHART_HEIGHT)
    st.plotly_chart(fig_bcat, use_container_width=True)

# =======================================================
# GRÁFICO 3 — Preço médio por Marca (1 categoria) + seleção de marcas
# =======================================================
st.markdown(f"<h3 style='font-size:{SECTION_TITLE_SIZE}px;margin:1rem 0 .25rem 0;'>Preço médio por Marca (por categoria)</h3>", unsafe_allow_html=True)
cat_bybrand = st.selectbox("Categoria (Preço por Marca)", options=cats, index=cats.index(sel_cat_kpi) if sel_cat_kpi in cats else 0)
df_bb_all = df[df["categoria"] == cat_bybrand].copy()
brands_cat = sorted(df_bb_all["marca"].dropna().unique().tolist())
sel_brands_bb = st.multiselect("Marcas a exibir", options=brands_cat, default=brands_cat)

df_bb = df_bb_all[df_bb_all["marca"].isin(sel_brands_bb)]
if df_bb.empty:
    st.info("Sem dados para os filtros atuais.")
else:
    by_brand = df_bb.groupby("marca", as_index=False)["preco"].mean().rename(columns={"preco":"preco_medio"})
    fig_bbrand = px.bar(
        by_brand.sort_values("preco_medio", ascending=False),
        x="marca", y="preco_medio",
        color="marca", color_discrete_sequence=SEQ,
        labels={"marca":"Marca", "preco_medio":"Preço médio (R$)"},
        title=f"Preço médio por Marca — {cat_bybrand}"
    )
    fig_bbrand.update_traces(texttemplate="%{y:.2f}", textposition="outside")
    fig_bbrand.update_layout(showlegend=False, xaxis_tickangle=-20,
                             legend=dict(font=dict(size=LEGEND_FONT_SIZE, color=text_color())))
    style_axes(fig_bbrand, height=CHART_HEIGHT)
    st.plotly_chart(fig_bbrand, use_container_width=True)

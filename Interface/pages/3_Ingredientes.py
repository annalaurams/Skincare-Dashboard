# /home/usuario/Área de trabalho/Dados/Interface/pages/3_Ingredientes.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import pandas as pd
import streamlit as st
import plotly.express as px

from core.data import load_data, unique_count_from_semicolon
from core.theme import apply_base_theme, apply_palette_css, color_sequence
from ui_components.filters import pick_marcas, pick_categorias

st.set_page_config(page_title="Skincare • Ingredientes", page_icon="🧪", layout="wide")

# =======================
# Aparência (edite aqui)
# =======================
TITLE_TEXT         = "Análise de Ingredientes"
TAGLINE_TEXT       = "Explore os ingredientes mais usados e compare por categorias e marcas."
TITLE_SIZE         = 32
TAGLINE_SIZE       = 16
SECTION_TITLE_SIZE = 20
KPI_HEIGHT_PX      = 110
KPI_BORDER_PX      = 3
LIST_FONT_PX       = 14
LIST_MIN_H_PX      = 120
CHART_HEIGHT       = 420
AXIS_TITLE_SIZE    = 16
AXIS_TICK_SIZE     = 13

# =======================
# Tema claro + paleta (persistente)
# =======================
if "palette_name" not in st.session_state:
    st.session_state["palette_name"] = "Roxo & Rosa"

apply_base_theme()  # claro fixo
apply_palette_css(st.session_state["palette_name"])
SEQ = color_sequence(st.session_state["palette_name"])

def accent(i=0): return SEQ[i % len(SEQ)] if SEQ else "#6e56cf"
def text_color(): return "#262730"
def subtext_color(): return "#555"
def panel_bg(): return "#ffffff"
def neutral_border(): return "#e6e6e6"

# =======================
# Helpers
# =======================
def split_semicolon(s: str) -> list[str]:
    if not isinstance(s, str) or not s.strip():
        return []
    return [p.strip() for p in s.split(";") if p.strip()]

def pct(v: float) -> str:
    try:
        return f"{100*v:.1f}%"
    except Exception:
        return "—"

# =======================
# Dados & filtros gerais
# =======================
df = load_data()

st.markdown(
    f"<h1 class='themed-title' style='margin:0; font-size:{TITLE_SIZE}px'>{TITLE_TEXT}</h1>",
    unsafe_allow_html=True
)
st.markdown(
    f"""
    <div style="margin:.4rem 0 1rem 0; padding:.6rem .9rem;
                background:linear-gradient(90deg,{accent(0)}10,{accent(1)}10);
                border:1px dashed {accent(0)}55; border-radius:12px; color:{subtext_color()};
                font-size:{TAGLINE_SIZE}px;">
      {TAGLINE_TEXT}
    </div>
    """,
    unsafe_allow_html=True
)

c1, c2 = st.columns(2)
with c1:
    sel_cats = pick_categorias(df, key_prefix="ing")
with c2:
    sel_marcas = pick_marcas(df, key_prefix="ing")

# Busca/ordem para a seção Top 10
busca = st.text_input("🔎 Buscar ingredientes...", "")
ordem = st.selectbox("Ordenar por", ["Mais frequente", "Nome (A–Z)", "Nome (Z–A)"], index=0)

# Aplica filtros gerais
df_f = df.copy()
if sel_cats:   df_f = df_f[df_f["categoria"].isin(sel_cats)]
if sel_marcas: df_f = df_f[df_f["marca"].isin(sel_marcas)]

# Explode ingredientes
rows = []
for _, r in df_f.iterrows():
    for ing in split_semicolon(r.get("ingredientes", "")):
        rows.append({"ingrediente": ing, "produto": r["nome"], "marca": r["marca"], "categoria": r["categoria"]})
df_ing = pd.DataFrame(rows)

# =======================
# KPIs (cards com borda)
# =======================
total_ing = unique_count_from_semicolon(df_f["ingredientes"]) if not df_f.empty else 0
if df_ing.empty:
    ing_mais, pct_mais = "—", "—"
else:
    freq = df_ing.groupby("ingrediente")["produto"].nunique().sort_values(ascending=False)
    ing_mais = freq.index[0]
    pct_mais = pct(freq.iloc[0] / max(1, df_f["nome"].nunique()))

def kpi_card(title: str, value: str, helper: str = "", color_idx: int = 0):
    st.markdown(
        f"""
        <div style="border:{KPI_BORDER_PX}px solid {accent(color_idx)}; border-radius:16px;
                    background:{panel_bg()}; padding:14px 16px; height:{KPI_HEIGHT_PX}px;
                    display:flex; flex-direction:column; justify-content:center;">
          <span style="font-size:{TAGLINE_SIZE-2}px; color:{subtext_color()};">{title}</span>
          <div style="font-weight:800; font-size:{TITLE_SIZE-14}px; color:{text_color()};">{value}</div>
          <span style="font-size:{TAGLINE_SIZE-3}px; color:{subtext_color()};">{helper}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

k1, k2, k3, k4 = st.columns(4)
with k1: kpi_card("Total de Ingredientes", f"{total_ing}", "ingredientes únicos", 0)
with k2: kpi_card("Mais frequente", pct_mais, ing_mais, 1)
with k3: kpi_card("Produtos (após filtros)", f"{df_f['nome'].nunique()}", "", 2)
with k4: kpi_card("Categorias (após filtros)", f"{df_f['categoria'].nunique()}", "", 3)

st.markdown("")

# =======================
# Base agregada por ingrediente
# =======================
if df_ing.empty:
    base = pd.DataFrame(columns=["ingrediente", "produtos", "marcas", "pct_produtos"])
else:
    base = (
        df_ing.groupby("ingrediente")
              .agg(produtos=("produto","nunique"), marcas=("marca","nunique"))
              .reset_index()
    )
    total_prod = max(1, df_f["nome"].nunique())
    base["pct_produtos"] = base["produtos"] / total_prod

# Busca/ordem
if not base.empty and busca.strip():
    base = base[base["ingrediente"].str.contains(busca.strip(), case=False, na=False)]
if not base.empty:
    if ordem == "Mais frequente":
        base = base.sort_values(["produtos","ingrediente"], ascending=[False, True])
    elif ordem == "Nome (A–Z)":
        base = base.sort_values("ingrediente")
    else:
        base = base.sort_values("ingrediente", ascending=False)

# =======================
# TOP 10 – Lista (visual) ou Planilha
# =======================
st.subheader("Top 10 Ingredientes Mais Utilizados")
modo_top = st.radio("Exibir como", ["Lista", "Planilha"], horizontal=True)
if base.empty:
    st.info("Sem ingredientes após os filtros.")
else:
    top10 = base.head(10).reset_index(drop=True)
    if modo_top == "Lista":
        for idx, row in top10.iterrows():
            frac = float(row["pct_produtos"])
            st.markdown(
                f"""
                <div style="border:{KPI_BORDER_PX}px solid {accent(1)}; border-radius:14px;
                            padding:10px 12px; margin-bottom:10px; background:{panel_bg()};
                            display:flex; align-items:center; gap:12px; min-height:{LIST_MIN_H_PX}px;">
                  <div style="min-width:32px; height:32px; border-radius:999px; display:flex;
                              align-items:center; justify-content:center; font-weight:800;
                              color:white; background:{accent(0)};">{idx+1}</div>
                  <div style="flex:1; font-size:{LIST_FONT_PX}px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                      <span style="font-weight:700; color:{text_color()};">{row['ingrediente']}</span>
                      <span style="opacity:.7;">{row['produtos']} produtos</span>
                    </div>
                    <div style="height:8px; border-radius:999px; background:{neutral_border()};
                                margin-top:8px; overflow:hidden;">
                      <div style="width:{frac*100:.1f}%; height:100%; background:{accent(0)};"></div>
                    </div>
                    <div style="margin-top:4px; opacity:.75;">
                      {pct(frac)} dos produtos • {row['marcas']} marcas
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        tbl = top10.copy()
        tbl["% dos produtos"] = (tbl["pct_produtos"]*100).map(lambda x: f"{x:.1f}%")
        tbl = tbl[["ingrediente","produtos","marcas","% dos produtos"]]
        tbl.columns = ["Ingrediente","Produtos","Marcas","% dos produtos"]
        st.dataframe(tbl, use_container_width=True)

st.markdown("---")

# =======================
# Gráfico: Ingredientes únicos por Categoria (com filtro de marca)
# =======================
st.subheader("Ingredientes por Categoria")
if df_ing.empty:
    st.info("Sem dados para exibir.")
else:
    marcas_opts = sorted(df_f["marca"].dropna().unique())
    marcas_graf = st.multiselect("Filtrar marcas no gráfico", options=marcas_opts, default=marcas_opts)
    df_g = df_f[df_f["marca"].isin(marcas_graf)] if marcas_graf else df_f

    rows_g = []
    for _, r in df_g.iterrows():
        for ing in split_semicolon(r.get("ingredientes","")):
            rows_g.append({"ingrediente": ing, "categoria": r["categoria"]})
    df_ing_g = pd.DataFrame(rows_g)

    if df_ing_g.empty:
        st.info("Sem dados para este filtro de marcas.")
    else:
        by_cat = (
            df_ing_g.groupby("categoria")["ingrediente"].nunique()
                    .reset_index(name="ingredientes_unicos")
                    .sort_values("ingredientes_unicos", ascending=False)
        )

        fig = px.bar(
            by_cat, x="categoria", y="ingredientes_unicos",
            color="categoria", color_discrete_sequence=SEQ,
            labels={"categoria":"Categoria","ingredientes_unicos":"Nº de ingredientes únicos"},
            title="Ingredientes únicos por categoria"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            showlegend=False, height=CHART_HEIGHT, xaxis_tickangle=-20,
            font=dict(color=text_color()),
            xaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE, color=text_color()),
                       tickfont=dict(size=AXIS_TICK_SIZE, color=text_color())),
            yaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE, color=text_color()),
                       tickfont=dict(size=AXIS_TICK_SIZE, color=text_color())),
            paper_bgcolor=panel_bg(), plot_bgcolor=panel_bg(),
            title_font_color=text_color()
        )
        st.plotly_chart(fig, use_container_width=True)

st.caption("Dica: use os filtros e ajuste a busca/ordem para destacar o que você precisa.")

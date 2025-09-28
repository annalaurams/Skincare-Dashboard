# /home/usuario/Área de trabalho/Dados/Interface/pages/4_Beneficios.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import pandas as pd
import streamlit as st
import plotly.express as px

from core.data import load_data, unique_count_from_semicolon
from core.theme import apply_base_theme, apply_palette_css, PALETTE_OPTIONS, color_sequence
from ui_components.filters import pick_marcas, pick_categorias

st.set_page_config(page_title="Skincare • Benefícios", page_icon="✨", layout="wide")

# =============== THEME / PALETTE ===============
if "base_theme" not in st.session_state:
    st.session_state["base_theme"] = "Claro"
if "palette_name" not in st.session_state:
    st.session_state["palette_name"] = PALETTE_OPTIONS[0]
apply_base_theme(st.session_state["base_theme"])
apply_palette_css(st.session_state["palette_name"])
seq = color_sequence(st.session_state["palette_name"])

def accent(i=0): return seq[i % len(seq)] if seq else "#6e56cf"
def text_color(): return "#111" if st.session_state["base_theme"] == "Claro" else "#f5f5f5"
def subtext_color(): return "#555" if st.session_state["base_theme"] == "Claro" else "#cfcfcf"
def panel_bg(): return "#fff" if st.session_state["base_theme"] == "Claro" else "#1f1f1f"
def neutral_border(): return "#e6e6e6" if st.session_state["base_theme"] == "Claro" else "#2a2a2a"

# =============== SIDEBAR CONTROLES ===============
st.sidebar.subheader("Aparência")
BORDER_PX  = st.sidebar.slider("Espessura da borda (px)", 1, 8, 3, 1)
CARD_FONT  = st.sidebar.slider("Tamanho da fonte da lista (px)", 10, 22, 14, 1)
CARD_MIN_H = st.sidebar.slider("Altura mínima da lista/cards (px)", 80, 220, 120, 10)

# =============== HELPERS ===============
def split_semicolon(s: str) -> list[str]:
    if not isinstance(s, str) or not s.strip():
        return []
    return [p.strip() for p in s.split(";") if p.strip()]

def pct(v: float) -> str:
    try:
        return f"{100*v:.1f}%"
    except Exception:
        return "—"

# =============== DADOS & FILTROS GERAIS ===============
df = load_data()

st.markdown(f"<h1 style='margin:0;color:{accent(0)}'>Análise de Benefícios</h1>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="margin:.4rem 0 1rem 0; padding:.6rem .9rem;
                background:linear-gradient(90deg,{accent(0)}10,{accent(1)}10);
                border:1px dashed {accent(0)}55; border-radius:12px; color:{subtext_color()};
                font-size:1rem;">
      Explore os benefícios mais usados e compare por categorias e marcas.
    </div>
    """,
    unsafe_allow_html=True
)

c1, c2 = st.columns(2)
with c1:
    sel_cats = pick_categorias(df, key_prefix="ben")
with c2:
    sel_marcas = pick_marcas(df, key_prefix="ben")

# Busca/ordem para a seção Top 10
busca = st.text_input("🔎 Buscar benefícios...", "")
ordem = st.selectbox("Ordenar por", ["Mais frequente", "Nome (A–Z)", "Nome (Z–A)"], index=0)

# Aplica filtros gerais
df_f = df.copy()
if sel_cats:   df_f = df_f[df_f["categoria"].isin(sel_cats)]
if sel_marcas: df_f = df_f[df_f["marca"].isin(sel_marcas)]

# Explode benefícios
rows = []
for _, r in df_f.iterrows():
    for ben in split_semicolon(r.get("beneficios", "")):
        rows.append({"beneficio": ben, "produto": r["nome"], "marca": r["marca"], "categoria": r["categoria"]})
df_ben = pd.DataFrame(rows)

# =============== KPIs (cards com borda) ===============
total_ben = unique_count_from_semicolon(df_f["beneficios"]) if not df_f.empty else 0
if df_ben.empty:
    ben_mais, pct_mais = "—", "—"
else:
    freq = df_ben.groupby("beneficio")["produto"].nunique().sort_values(ascending=False)
    ben_mais = freq.index[0]
    pct_mais = pct(freq.iloc[0] / max(1, df_f["nome"].nunique()))

def kpi_card(title: str, value: str, helper: str = ""):
    st.markdown(
        f"""
        <div style="border:{BORDER_PX}px solid {accent(0)}; border-radius:16px;
                    background:{panel_bg()}; padding:14px 16px; height:110px;
                    display:flex; flex-direction:column; justify-content:center;">
          <span style="font-size:.9rem; color:{subtext_color()};">{title}</span>
          <div style="font-weight:800; font-size:1.8rem; color:{text_color()};">{value}</div>
          <span style="font-size:.8rem; color:{subtext_color()};">{helper}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

k1, k2, k3, k4 = st.columns(4)
with k1: kpi_card("Total de Benefícios", f"{total_ben}", "benefícios únicos")
with k2: kpi_card("Mais frequente", pct_mais, ben_mais)
with k3: kpi_card("Produtos (após filtros)", f"{df_f['nome'].nunique()}")
with k4: kpi_card("Categorias (após filtros)", f"{df_f['categoria'].nunique()}")

st.markdown("")

# =============== BASE AGREGADA POR BENEFÍCIO ===============
if df_ben.empty:
    base = pd.DataFrame(columns=["beneficio", "produtos", "marcas", "pct_produtos"])
else:
    base = (df_ben.groupby("beneficio")
                .agg(produtos=("produto","nunique"), marcas=("marca","nunique"))
                .reset_index())
    total_prod = max(1, df_f["nome"].nunique())
    base["pct_produtos"] = base["produtos"] / total_prod

# Busca/ordem
if not base.empty and busca.strip():
    base = base[base["beneficio"].str.contains(busca.strip(), case=False, na=False)]
if not base.empty:
    if ordem == "Mais frequente":
        base = base.sort_values(["produtos","beneficio"], ascending=[False, True])
    elif ordem == "Nome (A–Z)":
        base = base.sort_values("beneficio")
    else:
        base = base.sort_values("beneficio", ascending=False)

# =============== TOP 10: Lista (ajustável) OU Planilha ===============
st.subheader("Top 10 Benefícios Mais Utilizados")
modo_top = st.radio("Exibir como", ["Lista", "Planilha"], horizontal=True)
if base.empty:
    st.info("Sem benefícios após os filtros.")
else:
    top10 = base.head(10).reset_index(drop=True)
    if modo_top == "Lista":
        for idx, row in top10.iterrows():
            frac = float(row["pct_produtos"])
            st.markdown(
                f"""
                <div style="border:{BORDER_PX}px solid {accent(1)}; border-radius:14px;
                            padding:10px 12px; margin-bottom:10px; background:{panel_bg()};
                            display:flex; align-items:center; gap:12px; min-height:{CARD_MIN_H}px;">
                  <div style="min-width:32px; height:32px; border-radius:999px; display:flex;
                              align-items:center; justify-content:center; font-weight:800;
                              color:white; background:{accent(0)};">{idx+1}</div>
                  <div style="flex:1; font-size:{CARD_FONT}px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                      <span style="font-weight:700; color:{text_color()};">{row['beneficio']}</span>
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
        tbl = tbl[["beneficio","produtos","marcas","% dos produtos"]]
        tbl.columns = ["Benefício","Produtos","Marcas","% dos produtos"]
        st.dataframe(tbl, use_container_width=True)

st.markdown("---")

# =============== GRÁFICO ÚNICO: BENEFÍCIOS POR CATEGORIA (com filtro de marca) ===============
st.subheader("Benefícios por Categoria")
if df_ben.empty:
    st.info("Sem dados para exibir.")
else:
    marcas_opts = sorted(df_f["marca"].dropna().unique())
    marcas_graf = st.multiselect("Filtrar marcas no gráfico", options=marcas_opts, default=marcas_opts)
    df_g = df_f[df_f["marca"].isin(marcas_graf)] if marcas_graf else df_f

    # Reexplode para o gráfico
    rows_g = []
    for _, r in df_g.iterrows():
        for ben in split_semicolon(r.get("beneficios","")):
            rows_g.append({"beneficio": ben, "categoria": r["categoria"]})
    df_ben_g = pd.DataFrame(rows_g)

    if df_ben_g.empty:
        st.info("Sem dados para este filtro de marcas.")
    else:
        by_cat = (df_ben_g.groupby("categoria")["beneficio"].nunique()
                  .reset_index(name="beneficios_unicos")
                  .sort_values("beneficios_unicos", ascending=False))

        fig = px.bar(
            by_cat, x="categoria", y="beneficios_unicos",
            color="categoria", color_discrete_sequence=seq,
            labels={"categoria":"Categoria","beneficios_unicos":"Nº de benefícios únicos"},
            title="Benefícios únicos por categoria"
        )
        fig.update_layout(showlegend=False, height=420, xaxis_tickangle=-20,
                          font=dict(color=text_color()),
                          paper_bgcolor=panel_bg(), plot_bgcolor=panel_bg(),
                          title_font_color=text_color())
        st.plotly_chart(fig, use_container_width=True)

# =============== CARDS DE DETALHES (opcional, mesmo layout dos ingredientes) ===============
st.markdown("---")
st.subheader("Detalhes de Benefícios")
if base.empty:
    st.info("Aqui aparecerão os benefícios com mais presença e seus detalhes.")
else:
    sample = base.head(6)
    cols = st.columns(3)
    for i, row in sample.iterrows():
        ben = row["beneficio"]
        sub = df_ben[df_ben["beneficio"] == ben]
        n_prod = int(row["produtos"])
        n_marcas = int(row["marcas"])
        cats = list(sub["categoria"].dropna().unique())[:8]
        with cols[i % 3]:
            st.markdown(
                f"""
                <div style="border:{BORDER_PX}px solid {accent(0)}; border-radius:16px;
                            padding:16px 18px; margin-bottom:12px; background:{panel_bg()};
                            min-height:{CARD_MIN_H}px; display:flex; flex-direction:column;">
                  <h4 style="margin:0 0 6px 0; color:{text_color()};">{ben}</h4>
                  <p style="margin:0 0 10px 0; color:{subtext_color()};">
                    {n_prod} produtos • {n_marcas} marcas
                  </p>
                  <div style="margin-top:auto;">
                    <div style="font-weight:600; margin-bottom:6px; color:{text_color()};">Categorias</div>
                    <div style="display:flex; flex-wrap:wrap; gap:6px;">
                      {''.join([f'<span style="font-size:12px; padding:4px 10px; border-radius:999px; color:{text_color()}; background:{accent((j%3))}25; border:1px solid {accent((j%3))};">{c}</span>' for j, c in enumerate(cats)]) or '<span style="opacity:.6;">—</span>'}
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )

st.caption("Dica: use os filtros e ajuste o tamanho da lista para destacar o que você precisa.")

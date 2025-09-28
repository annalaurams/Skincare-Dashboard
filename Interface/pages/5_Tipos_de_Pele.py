# /home/usuario/Área de trabalho/Dados/Interface/pages/5_Tipos_de_Pele.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import pandas as pd
import streamlit as st
import plotly.express as px

from core.data import load_data
from core.theme import apply_base_theme, apply_palette_css, PALETTE_OPTIONS, color_sequence
from ui_components.filters import pick_marcas, pick_categorias

st.set_page_config(page_title="Skincare • Tipos de Pele", page_icon="🧬", layout="wide")

# ========= TEMA =========
if "base_theme" not in st.session_state:
    st.session_state["base_theme"] = "Claro"
if "palette_name" not in st.session_state:
    st.session_state["palette_name"] = PALETTE_OPTIONS[0]
apply_base_theme(st.session_state["base_theme"])
apply_palette_css(st.session_state["palette_name"])
seq = color_sequence(st.session_state["palette_name"])

def accent(i=0): return seq[i % len(seq)] if seq else "#6e56cf"
def text_color(): return "#111111" if st.session_state["base_theme"] == "Claro" else "#f5f5f5"
def subtext_color(): return "#555555" if st.session_state["base_theme"] == "Claro" else "#cfcfcf"
def panel_bg(): return "#ffffff" if st.session_state["base_theme"] == "Claro" else "#1f1f1f"

# ========= CONSTANTES DE ESTILO (fixas no código) =========
CHART_H        = 580        # altura dos gráficos
FONT_TITLE_PX  = 24         # título dos gráficos
FONT_LABEL_PX  = 16         # rótulos/eixos
FONT_LEGEND_PX = 16         # legenda
BORDER_PX      = 3          # borda do card "mais frequente"
DONUT_HOLE     = 0.55       # abertura da rosca
BAR_GAP        = 0.06       # espaço entre barras (quanto menor, mais grossas)
BAR_GROUP_GAP  = 0.04       # espaço entre grupos (quanto menor, mais grossos)

# ========= HELPERS =========
def split_semicolon(s: str) -> list[str]:
    if not isinstance(s, str) or not s.strip(): return []
    return [p.strip() for p in s.split(";") if p.strip()]

# ========= DADOS =========
df = load_data()

st.markdown(f"<h1 style='margin:0;color:{accent(0)}'>Tipos de Pele</h1>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="margin:.35rem 0 1rem 0; padding:.6rem .9rem;
                background:linear-gradient(90deg,{accent(0)}10,{accent(1)}10);
                border:1px dashed {accent(0)}55; border-radius:12px; color:{subtext_color()};
                font-size:1rem;">
      Os filtros abaixo se aplicam a <b>toda a página</b>.
    </div>
    """,
    unsafe_allow_html=True
)

# Filtros (válidos para a página inteira)
c1, c2 = st.columns(2)
with c1:
    sel_marcas = pick_marcas(df, key_prefix="skin")
with c2:
    sel_cats = pick_categorias(df, key_prefix="skin")

df_f = df.copy()
if sel_marcas: df_f = df_f[df_f["marca"].isin(sel_marcas)]
if sel_cats:   df_f = df_f[df_f["categoria"].isin(sel_cats)]

# Explode tipos de pele
rows = []
for _, r in df_f.iterrows():
    tipos = split_semicolon(r.get("tipo_pele", "")) or ["(não informado)"]
    for t in tipos:
        rows.append({"tipo_pele": t, "nome": r["nome"], "marca": r["marca"], "categoria": r["categoria"]})
skin = pd.DataFrame(rows)

# ========= DISTRIBUIÇÃO (ROSCA) =========
st.markdown("### Distribuição dos Tipos de Pele")
if skin.empty:
    st.info("Sem dados após os filtros.")
else:
    base = (skin.groupby("tipo_pele")["nome"].nunique()
                 .reset_index(name="produtos")
                 .sort_values("produtos", ascending=False))
    total_prod = max(1, skin["nome"].nunique())
    base["pct"] = (base["produtos"] / total_prod * 100).round(1)

    fig = px.pie(
        base, names="tipo_pele", values="produtos", hole=DONUT_HOLE,
        color="tipo_pele", color_discrete_sequence=seq
    )
    # textos/legenda maiores
    fig.update_traces(textinfo="label+percent", textfont_size=FONT_LABEL_PX+4, pull=[0.02]*len(base))
    fig.update_layout(
        height=CHART_H,
        legend=dict(font=dict(size=FONT_LEGEND_PX)),
        font=dict(color=text_color()),
        paper_bgcolor=panel_bg(),
        plot_bgcolor=panel_bg(),
        title_font=dict(size=FONT_TITLE_PX, color=text_color()),
        margin=dict(t=30,b=20,l=10,r=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Card compacto "Tipo mais frequente"
    top = base.iloc[0]
    st.markdown(
        f"""
        <div style="
            border:{BORDER_PX}px solid {accent(0)};
            border-radius:14px; background:{panel_bg()};
            padding:12px 14px; margin-top:10px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-size:.85rem; color:{subtext_color()};">Tipo mais frequente</div>
              <div style="font-weight:800; font-size:1.4rem; color:{text_color()};">{top['tipo_pele']}</div>
            </div>
            <div style="font-weight:800; font-size:1.6rem; color:{accent(1)};">{top['pct']}%</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ========= TIPOS POR CATEGORIA (BARRAS) =========
st.markdown("---")
st.markdown("### Tipos de Pele por Categoria")
if skin.empty:
    st.info("Sem dados para exibir.")
else:
    by_cat = (skin.groupby(["categoria","tipo_pele"])["nome"].nunique()
                   .reset_index(name="produtos"))

    fig2 = px.bar(
        by_cat, x="categoria", y="produtos",
        color="tipo_pele", barmode="group",
        color_discrete_sequence=seq,
        labels={"categoria":"Categoria","produtos":"Nº de produtos","tipo_pele":"Tipo de pele"},
        title="Distribuição por categoria"
    )
    # barras mais “grossas”: diminuir gaps
    fig2.update_layout(
        height=CHART_H,
        bargap=BAR_GAP,
        bargroupgap=BAR_GROUP_GAP,
        legend_title_text="Tipo de pele",
        legend=dict(font=dict(size=FONT_LEGEND_PX)),
        xaxis=dict(title_font=dict(size=FONT_LABEL_PX+2), tickfont=dict(size=FONT_LABEL_PX)),
        yaxis=dict(title_font=dict(size=FONT_LABEL_PX+2), tickfont=dict(size=FONT_LABEL_PX)),
        font=dict(color=text_color()),
        paper_bgcolor=panel_bg(),
        plot_bgcolor=panel_bg(),
        title_font=dict(size=FONT_TITLE_PX, color=text_color()),
        margin=dict(t=40,b=30,l=10,r=10)
    )
    # (opcional) leve contorno nas barras
    for tr in fig2.data:
        tr.update(marker_line_width=0.4, marker_line_color="rgba(0,0,0,0.15)")
        # se quiser forçar ainda mais a espessura de cada barra, descomente:
        # tr.update(width=0.9)

    st.plotly_chart(fig2, use_container_width=True)

# ====== (Removido) gráficos/insights extras ======

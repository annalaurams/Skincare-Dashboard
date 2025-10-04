from __future__ import annotations
import sys
from pathlib import Path
from typing import List
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

from core.data import load_data
from core.theme import apply_base_theme, apply_palette_css, color_sequence

MODELS_DIR = "/home/usuario/Área de trabalho/Dados/models"
sys.path.append(MODELS_DIR)
try:
    from category import CATEGORY_CANONICAL_ORDER 
except Exception:
    CATEGORY_CANONICAL_ORDER = []
try:
    from benefit import BENEFICIOS_VALIDOS  
except Exception:
    BENEFICIOS_VALIDOS = []

st.set_page_config(page_title="Skincare • Benefícios", page_icon="✨", layout="wide")

TITLE_TEXT           = "Benefícios por Marca e Categoria"
TAGLINE_TEXT         = "Veja os benefícios mais presentes, compare marcas e descubra diferenciais por categoria."
TITLE_SIZE           = 60
TAGLINE_SIZE         = 26

SECTION_TITLE_SIZE   = 32
SUBTITLE_SIZE        = 22

CHART_HEIGHT         = 680
LEGEND_FONT_SIZE     = 30
TOOLTIP_FONT_SIZE    = 26
AXIS_TITLE_SIZE      = 24
AXIS_TICK_SIZE       = 22
BAR_TEXT_SIZE        = 18

WIDGET_HEIGHT_PX     = 48

if "palette_name" not in st.session_state:
    st.session_state["palette_name"] = "Solaris"

apply_base_theme()
apply_palette_css(st.session_state["palette_name"])
SEQ = color_sequence(st.session_state["palette_name"])

def accent(i=0): return SEQ[i % len(SEQ)] if SEQ else "#6e56cf"
def text_color(): return "#262730"
def subtext_color(): return "#555"
def panel_bg(): return "#ffffff"

st.markdown(f"""
<style>
.section-title {{ font-size:{SECTION_TITLE_SIZE}px; font-weight:700; color:{text_color()}; margin: 1rem 0 .5rem 0; }}
.subtle       {{ font-size:{TAGLINE_SIZE}px; color:{subtext_color()}; }}
.stSelectbox div[role="combobox"],
.stMultiSelect div[role="combobox"],
.stTextInput input, .stTextInput textarea {{
    min-height: {WIDGET_HEIGHT_PX}px !important;
    height: {WIDGET_HEIGHT_PX}px !important;
    font-size: 18px !important;
}}
div[data-baseweb="select"] {{ width: 100% !important; }}
[data-testid="stDataFrame"] thead tr th {{
    background: linear-gradient(90deg, {accent(0)}22, {accent(1)}22) !important;
    color: {text_color()} !important;
    font-weight: 800 !important;
    font-size: 16px !important;
}}
[data-testid="stDataFrame"] tbody td {{ font-size: 16px !important; }}
</style>
""", unsafe_allow_html=True)

def collapsed_label(lbl: str) -> dict:
    """Mantém label acessível e esconde visualmente (sem warnings)."""
    return {"label": lbl, "label_visibility": "collapsed"}

def _pretty_from_source(fname: str) -> str:
    stem = Path(fname).stem
    for suf in ["_products", "_skincare", "_cosmetics", "_dados"]:
        stem = stem.replace(suf, "")
    return stem.replace("_", " ").title()

def split_semicolon(s: str) -> List[str]:
    if not isinstance(s, str) or not s.strip():
        return []
    return [p.strip() for p in s.split(";") if p.strip()]

def explode_benefits(df_in: pd.DataFrame) -> pd.DataFrame:
    """Explode de benefícios; se houver lista oficial, filtra por ela."""
    rows = []
    valid = set(BENEFICIOS_VALIDOS) if BENEFICIOS_VALIDOS else None
    for _, r in df_in.iterrows():
        for ben in split_semicolon(r.get("beneficios", "")):
            if valid is not None and ben not in valid:
                continue
            rows.append({
                "beneficio": ben,
                "produto": r.get("nome"),
                "marca": r.get("marca"),
                "categoria": r.get("categoria"),
                "preco": r.get("preco"),
                "quantidade_valor": r.get("quantidade_valor"),
                "quantidade_unidade": r.get("quantidade_unidade"),
                "image_url": r.get("image_url") or r.get("imagem_url") or r.get("imagem"),
            })
    return pd.DataFrame(rows)

def pct_str(value: float, total: float) -> str:
    try:
        v = float(value) / float(max(total, 1))
        return f"{100*v:.1f}%"
    except Exception:
        return "—"

def brl(x):
    if x is None or pd.isna(x): return "—"
    return f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
def fmt_qtd(v, u):
    if pd.isna(v): return "—"
    try:
        v = float(v)
        vtxt = f"{int(v)}" if v.is_integer() else f"{v:.0f}" if v >= 100 else f"{v:.2f}"
    except Exception:
        vtxt = str(v)
    return f"{vtxt}{(' ' + u) if isinstance(u, str) and u else ''}"

#  Dados 
df = load_data()

uses_files = "_source_file" in df.columns and df["_source_file"].notna().any()
if uses_files:
    files = sorted(df["_source_file"].dropna().unique().tolist())
    LABEL_MAP = { _pretty_from_source(f): f for f in files }  # label -> arquivo
    BRAND_LABELS = list(LABEL_MAP.keys())
else:
    brands_col = sorted(df["marca"].dropna().unique().tolist()) if "marca" in df.columns else []
    LABEL_MAP = { b: b for b in brands_col }
    BRAND_LABELS = list(LABEL_MAP.keys())

CAT_CANON = CATEGORY_CANONICAL_ORDER[:] if CATEGORY_CANONICAL_ORDER else []
CAT_PRESENT = sorted(df["categoria"].dropna().unique().tolist())
CAT_OPTS = ["(todas)"] + (CAT_CANON if CAT_CANON else CAT_PRESENT)

st.markdown(f"<h1 style='margin:0; font-size:{TITLE_SIZE}px; color:{accent(0)}'>{TITLE_TEXT}</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='subtle' style='margin:.5rem 0 1.25rem 0;'>{TAGLINE_TEXT}</div>", unsafe_allow_html=True)

st.markdown(f"<div class='section-title'>Filtros</div>", unsafe_allow_html=True)
fc1, fc2, fc3 = st.columns([1.1, 1, 1.2])
with fc1:
    sel_brand_label = st.selectbox(**collapsed_label("Marca (obrigatório)"),
                                   options=BRAND_LABELS, index=0 if BRAND_LABELS else None)
    sel_brand_value = LABEL_MAP.get(sel_brand_label) if sel_brand_label else None
with fc2:
    sel_cat = st.selectbox(**collapsed_label("Categoria (opcional)"), options=CAT_OPTS, index=0)
with fc3:
    search_ben = st.text_input(**collapsed_label("Busca rápida (opcional)"), value="").strip()

if sel_brand_value is None:
    st.info("Selecione uma marca.")
    st.stop()

if uses_files:
    df_brand = df[df["_source_file"] == sel_brand_value].copy()
else:
    df_brand = df[df["marca"] == sel_brand_label].copy()
if sel_cat != "(todas)":
    df_brand = df_brand[df_brand["categoria"] == sel_cat]

# Resumo 
KPI_BORDER_PX = 3
def summary_card(title: str, value: str, subtitle: str, color_idx: int = 0):
    st.markdown(
        f"""
        <div style="
            border:{KPI_BORDER_PX}px solid {accent(color_idx)};
            border-radius:22px;
            padding:24px;
            background:{panel_bg()};
        ">
          <div style="color:{subtext_color()}; font-size:{SUBTITLE_SIZE}px;">{title}</div>
          <div style="font-weight:800; font-size:28px; color:{text_color()}; line-height:1; margin-top:4px;">
            {value}
          </div>
          <div style="color:{subtext_color()}; margin-top:2px;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(f"<div class='section-title'>Resumo</div>", unsafe_allow_html=True)

exp_brand = explode_benefits(df_brand)
total_ben_distintos = exp_brand["beneficio"].nunique() if not exp_brand.empty else 0

# benefício mais usado
if exp_brand.empty:
    top_ben, top_count = "—", 0
else:
    top_s = (exp_brand.groupby("beneficio")["produto"].nunique()
             .sort_values(ascending=False))
    top_ben = top_s.index[0]; top_count = int(top_s.iloc[0])

# benefício exclusivo na marca (só ela possui)
exp_all = explode_benefits(df)
exclusivos = []
if not exp_brand.empty:
    set_marca = set(exp_brand["beneficio"].unique())
    by_brand = exp_all.groupby(["beneficio"])["marca"].nunique()
    exclusivos = [b for b in set_marca if by_brand.get(b, 0) == 1]
ex_ben = exclusivos[0] if exclusivos else "—"

k1, k2, k3 = st.columns(3)
with k1:
    summary_card("Benefícios distintos", str(total_ben_distintos), "na marca selecionada", color_idx=0)
with k2:
    summary_card("Benefício mais usado", top_ben, f"{top_count} produto(s)", color_idx=1)
with k3:
    summary_card("Benefício exclusivo", ex_ben, "apenas nesta marca", color_idx=2)

st.markdown("---")

#  1) Distribuição de Benefícios — Barras/Rosca (+ filtro) 
st.markdown(f"<div class='section-title'>Distribuição de Benefícios</div>", unsafe_allow_html=True)

exp_dist = explode_benefits(df_brand)
total_produtos_contexto = df_brand["nome"].nunique()

if BENEFICIOS_VALIDOS:
    ben_present = [b for b in BENEFICIOS_VALIDOS if b in set(exp_dist["beneficio"].unique())]
else:
    ben_present = sorted(exp_dist["beneficio"].dropna().unique().tolist()) if not exp_dist.empty else []

c1, c2 = st.columns([1.0, 1.0])
with c1:
    view_opt = st.radio(**collapsed_label("Visualização (benefícios)"),
                        options=["Barras", "Rosca"], horizontal=True, key="ben_view")
with c2:
    ben_mode = st.radio(**collapsed_label("Benefícios (modo)"),
                        options=["(Todos)", "Selecionar"], horizontal=True, key="ben_mode")

sel_bens_multi: List[str] = []
if ben_mode == "Selecionar":
    sel_bens_multi = st.multiselect(**collapsed_label("Benefícios (seleção múltipla)"),
                                    options=ben_present, default=ben_present[:10])

# aplica “Busca rápida” e seleção multi
if search_ben:
    exp_dist = exp_dist[exp_dist["beneficio"].str.contains(search_ben, case=False, na=False)]
if ben_mode == "Selecionar" and sel_bens_multi:
    exp_dist = exp_dist[exp_dist["beneficio"].isin(sel_bens_multi)]

if exp_dist.empty or total_produtos_contexto == 0:
    st.info("Sem dados para exibir a distribuição.")
else:
    by_ben = (exp_dist.groupby("beneficio")["produto"]
              .nunique().reset_index(name="qtd_produtos"))
    by_ben["pct"] = by_ben["qtd_produtos"] / float(total_produtos_contexto)
    by_ben = by_ben.sort_values(["qtd_produtos", "beneficio"], ascending=[False, True])

    if view_opt == "Barras":
        fig = px.bar(
            by_ben, x="beneficio", y="qtd_produtos",
            text="qtd_produtos",
            color="beneficio", color_discrete_sequence=SEQ,
            labels={"beneficio": "Benefício", "qtd_produtos": "Quantos Produtos"},
            hover_data={}
        )
        fig.update_traces(
            textposition="outside",
            textfont=dict(size=BAR_TEXT_SIZE, color="#363636"),
            hovertemplate="<b>%{x}</b><br>Produtos: %{y} de " + str(total_produtos_contexto) +
                          "<br>Participação: %{customdata[0]}<extra></extra>",
            customdata=np.array([[pct_str(v, total_produtos_contexto)] for v in by_ben["qtd_produtos"]])
        )
        fig.update_layout(
            height=CHART_HEIGHT, showlegend=False,
            xaxis_tickangle=-20,
            xaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=AXIS_TICK_SIZE)),
            yaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=AXIS_TICK_SIZE)),
            hoverlabel=dict(font_size=TOOLTIP_FONT_SIZE),
            margin=dict(t=40, b=120, l=30, r=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        figp = px.pie(
            by_ben, names="beneficio", values="qtd_produtos",
            hole=0.55, color_discrete_sequence=SEQ
        )
        figp.update_traces(
            textposition="inside", texttemplate="%{percent:.1%}",
            hovertemplate="<b>%{label}</b><br>Produtos: %{value} de " + str(total_produtos_contexto) +
                          "<br>Participação: %{percent:.1%}<extra></extra>"
        )
        figp.update_layout(
            height=CHART_HEIGHT,
            legend=dict(font=dict(size=LEGEND_FONT_SIZE)),
            hoverlabel=dict(font_size=TOOLTIP_FONT_SIZE),
            margin=dict(t=40, b=40, l=40, r=40)
        )
        st.plotly_chart(figp, use_container_width=True)

st.markdown("---")

#  2) Top 5 Benefícios 
st.markdown(f"<div class='section-title'>Top 5 Benefícios</div>", unsafe_allow_html=True)

if exp_dist.empty or total_produtos_contexto == 0:
    st.info("Sem dados para exibir o Top 5.")
else:
    top5 = (exp_dist.groupby("beneficio")["produto"].nunique()
            .reset_index(name="qtd_produtos")
            .sort_values(["qtd_produtos", "beneficio"], ascending=[False, True])
            .head(5))
    top5["pct"] = top5["qtd_produtos"] / float(total_produtos_contexto)

    figt = px.bar(
        top5.sort_values(["qtd_produtos","beneficio"], ascending=[True, True]),
        x="qtd_produtos", y="beneficio",
        orientation="h",
        text="qtd_produtos",
        color="beneficio", color_discrete_sequence=SEQ,
        labels={"qtd_produtos": "Quantidade de Produtos", "beneficio": "Benefício"},
        hover_data={}
    )
    figt.update_traces(
        textposition="outside",
        textfont=dict(size=BAR_TEXT_SIZE, color="#363636"),
        hovertemplate="<b>%{y}</b><br>Produtos: %{x} de " + str(total_produtos_contexto) +
                      "<br>Participação: %{customdata[0]}<extra></extra>",
        customdata=np.array([[pct_str(v, total_produtos_contexto)] for v in top5["qtd_produtos"]])
    )
    figt.update_layout(
        height=CHART_HEIGHT//1.4, showlegend=False,
        xaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=AXIS_TICK_SIZE)),
        yaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=AXIS_TICK_SIZE)),
        hoverlabel=dict(font_size=TOOLTIP_FONT_SIZE),
        margin=dict(t=40, b=40, l=140, r=40)
    )
    st.plotly_chart(figt, use_container_width=True)

st.markdown("---")

#  3) Benefícios por Categoria (heatmap) com seleção 1..10 
st.markdown(f"<div class='section-title'>Benefícios por Categoria</div>", unsafe_allow_html=True)

if uses_files:
    exp_brand_allcats = explode_benefits(df[df["_source_file"] == sel_brand_value])
else:
    exp_brand_allcats = explode_benefits(df[df["marca"] == sel_brand_label])

if exp_brand_allcats.empty:
    st.info("Sem benefícios para construir o mapa por categoria.")
    st.stop()

cat_all = exp_brand_allcats["categoria"].dropna().unique().tolist()
if CATEGORY_CANONICAL_ORDER:
    can_set = set(CATEGORY_CANONICAL_ORDER)
    cat_sorted = [c for c in CATEGORY_CANONICAL_ORDER if c in cat_all] + [c for c in sorted(cat_all) if c not in can_set]
else:
    cat_sorted = sorted(cat_all)

default_cats = cat_sorted[:min(10, len(cat_sorted))]
sel_cats_hm = st.multiselect(
    **collapsed_label("Categorias (heatmap)"),
    options=cat_sorted,
    default=default_cats,
    max_selections=10,
    help="Escolha de 1 a 10 categorias para o mapa de calor."
)
if not sel_cats_hm:
    st.warning("Selecione pelo menos uma categoria para exibir o mapa.")
    st.stop()

exp_brand_allcats = exp_brand_allcats[exp_brand_allcats["categoria"].isin(sel_cats_hm)]

if ben_mode == "Selecionar" and sel_bens_multi:
    exp_brand_allcats = exp_brand_allcats[exp_brand_allcats["beneficio"].isin(sel_bens_multi)]
elif search_ben:
    exp_brand_allcats = exp_brand_allcats[exp_brand_allcats["beneficio"].str.contains(search_ben, case=False, na=False)]

if exp_brand_allcats.empty:
    st.info("Sem benefícios para o mapa por categoria com os filtros atuais.")
else:
    if ben_mode == "Selecionar" and sel_bens_multi:
        ben_focus = sel_bens_multi
    else:
        N_TOP = 12
        ben_focus = (exp_brand_allcats.groupby("beneficio")["produto"]
                     .nunique().sort_values(ascending=False).head(N_TOP).index.tolist())

    sub = exp_brand_allcats[exp_brand_allcats["beneficio"].isin(ben_focus)]
    pivot = (sub.groupby(["categoria", "beneficio"])["produto"]
             .nunique().unstack(fill_value=0))

    pivot = pivot.loc[[c for c in sel_cats_hm if c in pivot.index], :]

    n_seq = len(SEQ)
    if n_seq >= 18:
        block = n_seq // 4
        third_line = SEQ[2*block:3*block]
    else:
        third_line = SEQ

    custom_scale = [
        (0.0, "#ffffff"),
        (0.05, "#f0f0f0"),
        (0.15, "#d9d9d9"),
    ]
    steps = np.linspace(0.2, 1, len(third_line))
    for pos, color in zip(steps, third_line):
        custom_scale.append((float(pos), color))

    fig_hm = px.imshow(
        pivot,
        color_continuous_scale=custom_scale,
        aspect="auto",
        labels=dict(color="Produtos"),
        title=f"Categorias × Benefícios — {sel_brand_label}"
    )
    fig_hm.update_layout(font=dict(size=24))
    fig_hm.update_layout(
        height=CHART_HEIGHT,
        coloraxis_colorbar=dict(title="Produtos", tickfont=dict(size=AXIS_TICK_SIZE)),
        xaxis=dict(tickfont=dict(size=AXIS_TICK_SIZE)),
        yaxis=dict(tickfont=dict(size=AXIS_TICK_SIZE)),
        hoverlabel=dict(font_size=TOOLTIP_FONT_SIZE)
    )
    st.plotly_chart(fig_hm, use_container_width=True)

st.markdown("---")

#  4) Comparação entre Marcas 
st.markdown(f"<div class='section-title'>Comparação de Benefícios entre Marcas</div>", unsafe_allow_html=True)

comp_labels = st.multiselect(
    **collapsed_label("Marcas (comparação)"),
    options=BRAND_LABELS,
    default=[sel_brand_label],
    max_selections=3
)

cmp_ben_mode = st.radio(
    **collapsed_label("Benefícios (comparação)"),
    options=["(Todos)", "Selecionar"], horizontal=True, key="cmp_ben_mode"
)

cmp_opts: List[str] = []
if cmp_ben_mode == "Selecionar":
    if comp_labels:
        tmp = []
        for lab in comp_labels:
            val = LABEL_MAP[lab]
            base = df[df["_source_file"] == val] if uses_files else df[df["marca"] == lab]
            tmp.append(explode_benefits(base)[["beneficio"]])
        exist = sorted(pd.concat(tmp)["beneficio"].dropna().unique().tolist()) if tmp else []
        cmp_opts = [b for b in BENEFICIOS_VALIDOS if b in set(exist)] if BENEFICIOS_VALIDOS else exist
    else:
        exist = explode_benefits(df)["beneficio"].dropna().unique().tolist()
        cmp_opts = [b for b in BENEFICIOS_VALIDOS if b in set(exist)] if BENEFICIOS_VALIDOS else sorted(exist)

cmp_sel_bens: List[str] = []
if cmp_ben_mode == "Selecionar":
    cmp_sel_bens = st.multiselect(**collapsed_label("Benefícios (seleção múltipla)"),
                                  options=cmp_opts, default=cmp_opts[:10])

if comp_labels:
    dfs_comp = []
    for lab in comp_labels:
        val = LABEL_MAP[lab]
        base = df[df["_source_file"] == val] if uses_files else df[df["marca"] == lab]
        exp_ = explode_benefits(base)
        if cmp_ben_mode == "Selecionar" and cmp_sel_bens:
            exp_ = exp_[exp_["beneficio"].isin(cmp_sel_bens)]
        grp = (exp_.groupby("beneficio")["produto"].nunique().reset_index(name="produtos"))
        grp["marca_label"] = lab
        dfs_comp.append(grp)
    comp_df = pd.concat(dfs_comp, ignore_index=True) if dfs_comp else pd.DataFrame()
    if comp_df.empty:
        st.info("Sem dados para comparar.")
    else:
        if cmp_ben_mode == "(Todos)":
            N_TOP = 12
            topN = (comp_df.groupby("beneficio")["produtos"].sum()
                    .sort_values(ascending=False).head(N_TOP).index.tolist())
            comp_df = comp_df[comp_df["beneficio"].isin(topN)]
        fig_cmp = px.bar(
            comp_df,
            x="beneficio", y="produtos",
            color="marca_label", barmode="group",
            color_discrete_sequence=SEQ,  
            labels={"beneficio": "Benefício", "produtos": "Produtos", "marca_label": "Marca"}
        )
        fig_cmp.update_layout(
            height=CHART_HEIGHT,
            legend=dict(font=dict(size=LEGEND_FONT_SIZE)),
            xaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=AXIS_TICK_SIZE)),
            yaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=AXIS_TICK_SIZE)),
            hoverlabel=dict(font_size=TOOLTIP_FONT_SIZE),
            margin=dict(t=40, b=120, l=30, r=20)
        )
        st.plotly_chart(fig_cmp, use_container_width=True)
else:
    st.caption("Selecione 1 a 3 marcas para comparar.")

st.markdown("---")

#  5) Pesquisa por Benefício — cards estilizados 
st.markdown(
    f"<h3 style='font-size:{SECTION_TITLE_SIZE}px; margin:.75rem 0 .5rem 0; color:{accent(0)}'>Pesquisa por Benefício</h3>",
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div style="display:grid; grid-template-columns:1.3fr 1fr 1fr; gap:16px; align-items:end; margin:.25rem 0 .5rem 0;">
      <div><div style="font-size:20px; font-weight:700; color:{text_color()}; margin-bottom:6px;">Benefício</div></div>
      <div><div style="font-size:20px; font-weight:700; color:{text_color()}; margin-bottom:6px;">Marca</div></div>
      <div><div style="font-size:20px; font-weight:700; color:{text_color()}; margin-bottom:6px;">Categoria</div></div>
    </div>
    """,
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns([1.3, 1, 1])
with c1:
    q_ben = st.text_input(**collapsed_label("Benefício (pesquisa)"),
                          placeholder="Ex.: hidratação").strip()
with c2:
    p_brand_lab = st.selectbox(**collapsed_label("Marca (filtro)"),
                               options=["(todas)"] + BRAND_LABELS, index=0)
with c3:
    p_cat = st.selectbox(**collapsed_label("Categoria (filtro)"),
                         options=CAT_OPTS, index=0)

if not q_ben:
    st.caption("Dica: pesquise um benefício e filtre por marca/categoria para ver os produtos correspondentes.")
    st.stop()

df_p = df.copy()
if p_brand_lab != "(todas)":
    val = LABEL_MAP[p_brand_lab]
    df_p = df_p[df_p["_source_file"] == val] if uses_files else df_p[df_p["marca"] == p_brand_lab]
if p_cat != "(todas)":
    df_p = df_p[df_p["categoria"] == p_cat]

exp_p = explode_benefits(df_p)
hit = exp_p[exp_p["beneficio"].str.contains(q_ben, case=False, na=False)]
if hit.empty:
    st.info("Nenhum produto encontrado para esse benefício nos filtros atuais.")
    st.stop()

prods = (
    hit.groupby("produto")
       .agg(marca=("marca","first"),
            categoria=("categoria","first"))
       .reset_index()
       .rename(columns={"produto":"Produto","marca":"Marca","categoria":"Categoria"})
)

st.markdown(f"""
<style>
.product-card {{
  border: 2px solid #ececf1; border-radius: 14px;
  padding: 12px 16px; background: #fff;
  box-shadow: 0 2px 2px rgba(0,0,0,0.04);
  display: grid; grid-template-columns: 1.2fr .5fr 1fr; gap: 14px;
  align-items: center;
}}
.product-card + .product-card {{ margin-top: 10px; }}
.p-name {{ font-weight: 800; font-size: 22px; color: {text_color()}; line-height: 1.2; }}
.p-brand {{ font-size: 14px; color: #7a7a7a; margin-top: 2px; }}
.p-price {{ font-weight: 900; font-size: 22px; color: {accent(2)}; text-align: right; }}
.p-qty   {{ font-size: 14px; color:#777; text-align: right; }}
.p-pills {{ display:flex; gap:6px; flex-wrap:wrap; justify-content:flex-end; }}
.pill {{
  display:inline-block; padding: 4px 8px; border-radius: 999px;
  border:1px solid #e5e7eb; background:#f7f7fb; color:#313244;
  font-size: 12px; font-weight: 700;
}}
.pill.cat  {{ background: {accent(0)}22; border-color:{accent(0)}55; color:{accent(0)}; }}
.pill.hit  {{ background: {accent(1)}22; border-color:{accent(1)}55; color:{accent(1)}; }}
</style>
""", unsafe_allow_html=True)

base = df_p[df_p["nome"].isin(prods["Produto"])].copy()

# renderiza cards
for nome_prod in prods["Produto"].tolist():
    sub = base[base["nome"] == nome_prod]
    if sub.empty:
        continue
    row = sub.iloc[0]
    marca = row.get("marca", "—")
    categoria = row.get("categoria", "—")
    preco = brl(row.get("preco"))
    qty = fmt_qtd(row.get("quantidade_valor"), row.get("quantidade_unidade"))

    exp_one = explode_benefits(sub)
    ben_all = exp_one["beneficio"].dropna().unique().tolist()
    hit_mask = exp_one["beneficio"].str.contains(q_ben, case=False, na=False)
    ben_hits = exp_one.loc[hit_mask, "beneficio"].dropna().unique().tolist()

    # 2 destaques + 3 gerais
    ben_hits_show = ben_hits[:2]
    ben_others = [b for b in ben_all if b not in ben_hits_show][:3]

    st.markdown(
        f"""
        <div class="product-card">
          <div>
            <div class="p-name">{nome_prod}</div>
            <div class="p-brand">{marca}</div>
          </div>

          <div>
            <div class="p-price">{preco}</div>
            <div class="p-qty">{qty}</div>
          </div>

          <div class="p-pills">
            <span class="pill cat">{categoria}</span>
            {''.join(f'<span class="pill hit">{b}</span>' for b in ben_hits_show)}
            {''.join(f'<span class="pill">{b}</span>' for b in ben_others)}
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

from __future__ import annotations
import sys
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

from core.data import load_data
from core.theme import apply_base_theme, apply_palette_css, color_sequence

sys.path.append("/home/usuario/Área de trabalho/Dados/models")
try:
    from skin import SKIN_TYPE_SYNONYMS_PT, SKIN_TYPE_CANONICAL_ORDER
except Exception:
    SKIN_TYPE_SYNONYMS_PT = {}
    SKIN_TYPE_CANONICAL_ORDER = [
        "acneica","com cicatrizes","com celulite","com espinhas ativas","com flacidez",
        "com manchas","com olheiras","com poros dilatados","com rosacea","desidratada",
        "madura","mista","normal","oleosa","opaca","seca","sensível","radiante","reativa",
        "todos os tipos","(não informado)"
    ]
try:
    from category import CATEGORY_CANONICAL_ORDER
except Exception:
    CATEGORY_CANONICAL_ORDER = None

st.set_page_config(page_title="Skincare • Tipos de Pele", page_icon="🧬", layout="wide")

if "palette_name" not in st.session_state:
    st.session_state["palette_name"] = "Solaris"
apply_base_theme()
apply_palette_css(st.session_state["palette_name"])
SEQ = color_sequence(st.session_state["palette_name"])

def accent(i=0): return SEQ[i % len(SEQ)] if SEQ else "#6e56cf"
def text_color(): return "#262730"
def subtext_color(): return "#555"
def panel_bg(): return "#ffffff"
def neutral_border(): return "#ececf1"

TITLE_TEXT     = "Tipos de Pele"
TAGLINE_TEXT   = "Analise como os produtos são direcionados para diferentes tipos de pele"
TITLE_SIZE     = 60
TAGLINE_SIZE   = 26

FILTER_TITLE_SIZE   = 32
FILTER_LABEL_SIZE   = 18
FILTER_INPUT_SIZE   = 18
WIDGET_HEIGHT_PX    = 48

KPI_CARD_H     = 150
KPI_TITLE_PX   = 18
KPI_VALUE_PX   = 30
KPI_HELP_PX    = 14
KPI_RADIUS     = 16
KPI_SHADOW     = "0 10px 28px rgba(0,0,0,.08)"

CHART_H            = 680
AXIS_TITLE_SIZE    = 24
AXIS_TICK_SIZE     = 22
LEGEND_FONT_SIZE   = 30
TOOLTIP_FONT_SIZE  = 26
BAR_TEXT_SIZE      = 18
BARGAP             = 0.18
BARGROUPGAP        = 0.08

PILL_FONT          = 12

st.markdown(f"""
<style>
/* Títulos e textos */
.section-title {{ font-size:{FILTER_TITLE_SIZE}px; font-weight:700; color:{text_color()}; margin: 1rem 0 .5rem 0; }}
.subtle       {{ font-size:{TAGLINE_SIZE}px; color:{subtext_color()}; }}

/* Altura e fonte dos inputs */
.stSelectbox div[role="combobox"],
.stMultiSelect div[role="combobox"],
.stTextInput input, .stTextInput textarea {{
    min-height: {WIDGET_HEIGHT_PX}px !important;
    height: {WIDGET_HEIGHT_PX}px !important;
    font-size: {FILTER_INPUT_SIZE}px !important;
}}
.stRadio label, .stSelectbox label, .stTextInput label, .stMultiSelect label {{
    font-size:{FILTER_LABEL_SIZE}px !important; color:{text_color()} !important; font-weight:700 !important;
}}
div[data-baseweb="select"] {{ width: 100% !important; }}

/* KPI cards */
.kpi-box {{
  border:1px solid {neutral_border()}; border-radius:{KPI_RADIUS}px; background:{panel_bg()};
  box-shadow:{KPI_SHADOW}; padding:16px 18px; height:{KPI_CARD_H}px;
  display:flex; flex-direction:column; justify-content:center; gap:.25rem;
}}
.kpi-title {{ font-size:{KPI_TITLE_PX}px; color:{subtext_color()}; font-weight:700; }}
.kpi-value {{ font-size:{KPI_VALUE_PX}px; font-weight:900; color:{text_color()}; line-height:1; }}
.kpi-help  {{ font-size:{KPI_HELP_PX}px; color:{subtext_color()}; }}

/* Lista (Pesquisa) */
.list-wrap {{ border:1px solid {neutral_border()}; border-radius:12px; background:{panel_bg()}; padding:10px; }}
.row {{
  border:1px solid {neutral_border()}; border-radius:12px; background:{panel_bg()};
  padding:14px 16px; box-shadow:0 8px 22px rgba(0,0,0,.06);
  display:grid; grid-template-columns: 1.6fr .7fr 1.2fr; align-items:center; gap:12px; margin:8px 8px;
}}
.row + .row {{ margin-top:8px; }}
.r-left .name {{ font-weight:800; color:{text_color()}; font-size:22px; line-height:1.2; }}
.r-left .brand {{ color:{subtext_color()}; font-size:14px; margin-top:2px; }}
.pill {{ display:inline-block; padding:4px 10px; border-radius:999px; font-size:{PILL_FONT}px; color:{text_color()};
        background:{accent(0)}14; border:1px solid {accent(0)}55; }}
.r-price {{ font-weight:900; color:{accent(0)}; font-size:18px; text-align:right; }}
.r-qty   {{ color:{subtext_color()}; font-size:14px; text-align:right; }}
.r-mid   {{ color:{text_color()}; font-size:14px; }}

@media (max-width: 980px){{
  .row {{ grid-template-columns: 1fr; text-align:left; }}
  .r-price, .r-qty {{ text-align:left; }}
}}
</style>
""", unsafe_allow_html=True)

def split_semicolon(s: str) -> list[str]:
    if not isinstance(s, str) or not s.strip():
        return []
    return [p.strip() for p in s.split(";") if p.strip()]

def to_base_types(raw: str) -> list[str]:
    s = str(raw).lower()
    found = set()
    for canonical, syns in SKIN_TYPE_SYNONYMS_PT.items():
        for term in syns:
            if term and term.lower() in s:
                found.add(canonical.lower())
                break
    if "todos" in s and "tipo" in s:
        found.add("todos os tipos")
    return list(found) or ["(não informado)"]

def explode_skin(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        tipos_raw = split_semicolon(r.get("tipo_pele", "")) or ["(não informado)"]
        for t in tipos_raw:
            rows.append({
                "tipo_pele": t,
                "nome": r.get("nome"),
                "marca": r.get("marca"),
                "categoria": r.get("categoria"),
                "preco": r.get("preco"),
                "quantidade": r.get("quantidade"),
                "quantidade_valor": r.get("quantidade_valor"),
                "quantidade_unidade": r.get("quantidade_unidade"),
            })
    return pd.DataFrame(rows)

def qty_text(row: pd.Series) -> str:
    q = row.get("quantidade")
    qv = row.get("quantidade_valor")
    qu = row.get("quantidade_unidade")
    if isinstance(q, str) and q.strip():
        return q
    if pd.notna(qv) and isinstance(qu, str) and qu.strip():
        try: return f"{float(qv):g}{qu}"
        except Exception: return f"{qv}{qu}"
    return ""

def brl(x) -> str:
    try:
        if pd.isna(x): return "—"
        return f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"

def style_axes(fig, height: int = CHART_H):
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
        hoverlabel=dict(font_size=TOOLTIP_FONT_SIZE, font_color="black", bgcolor="white"),
    )
    return fig

df = load_data()

st.markdown(
    f"<h1 style='margin:0; font-size:{TITLE_SIZE}px; color:{accent(0)}'>{TITLE_TEXT}</h1>",
    unsafe_allow_html=True
)
st.markdown(
    f"<div class='subtle' style='margin:.35rem 0 1.0rem 0;'>{TAGLINE_TEXT}</div>",
    unsafe_allow_html=True
)

st.markdown(f"<div class='section-title'>Filtros</div>", unsafe_allow_html=True)

brands = sorted(df["marca"].dropna().unique().tolist())
cats_all = CATEGORY_CANONICAL_ORDER[:] if CATEGORY_CANONICAL_ORDER else sorted(df["categoria"].dropna().unique().tolist())

c1, c2, c3 = st.columns([1,1,1])
with c1:
    sel_brand = st.selectbox("Marca (obrigatório)", options=brands, index=0, key="flt_brand")
with c2:
    cat_opts_present = sorted(df[df["marca"] == sel_brand]["categoria"].dropna().unique().tolist())
    if CATEGORY_CANONICAL_ORDER:
        ordered = [c for c in CATEGORY_CANONICAL_ORDER if c in cat_opts_present]
        cat_opts = ["(todas)"] + ordered + [c for c in cat_opts_present if c not in ordered]
    else:
        cat_opts = ["(todas)"] + cat_opts_present
    sel_cat = st.selectbox("Categoria (opcional)", options=cat_opts, index=0, key="flt_cat")
with c3:
    q_skin = st.text_input("Buscar tipo de pele (opcional)",
                           placeholder="ex.: oleosa, sensível, todos os tipos",
                           key="flt_search")

df_scope = df[df["marca"] == sel_brand].copy()
if sel_cat != "(todas)":
    df_scope = df_scope[df_scope["categoria"] == sel_cat]

k1, k2, k3 = st.columns(3)
skin_expl = explode_skin(df_scope)
total_products_brand = df[df["marca"] == sel_brand]["nome"].nunique()

distinct_types = set()
for s in skin_expl["tipo_pele"].dropna().tolist():
    for b in to_base_types(s):
        distinct_types.add(b)

top_type = "—"; pct_top = "—"
if not skin_expl.empty:
    rows = []
    for prod, g in skin_expl.groupby("nome"):
        bases = set()
        for t in g["tipo_pele"]:
            bases.update(to_base_types(t))
        for b in bases:
            rows.append({"produto": prod, "tipo_base": b})
    pres = pd.DataFrame(rows)
    if not pres.empty:
        dist = pres.groupby("tipo_base")["produto"].nunique().sort_values(ascending=False)
        top_type = dist.index[0]
        pct_top = f"{(dist.iloc[0] / max(1, pres['produto'].nunique()) * 100):.1f}%"

df_brand_only = df[df["marca"] == sel_brand].copy()
brand_skin = explode_skin(df_brand_only)
rows_tt = []
for prod, g in brand_skin.groupby("nome"):
    bases = set()
    for t in g["tipo_pele"]:
        bases.update(to_base_types(t))
    rows_tt.append({"produto": prod, "todos": ("todos os tipos" in bases)})
pct_todos = f"{(pd.DataFrame(rows_tt)['todos'].mean() * 100):.1f}%" if rows_tt else "—"

# ====== KPIs ======
k1, k2, k3 = st.columns(3)
skin_expl = explode_skin(df_scope)
total_products_brand = df[df["marca"] == sel_brand]["nome"].nunique()

# ... (cálculos de distinct_types, top_type/pct_top e pct_todos permanecem iguais)

KPI_BORDER_PX = 3  # espessura da borda colorida

def summary_card(title: str, value: str, helper: str, color_idx: int = 0):
    st.markdown(
        f"""
        <div class="kpi-box" style="border:{KPI_BORDER_PX}px solid {accent(color_idx)};">
          <div class="kpi-title">{title}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-help">{helper}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k1:
    summary_card(
        "Tipos de pele cobertos (marca)",
        str(len(distinct_types)),
        f"Produtos analisados: {total_products_brand}",
        color_idx=0
    )
with k2:
    summary_card(
        "Tipo mais frequente (escopo)",
        top_type,
        f"Participação: {pct_top}",
        color_idx=1
    )
with k3:
    summary_card(
        "% “Todos os tipos” (marca)",
        pct_todos,
        "Considera todos os produtos da marca",
        color_idx=2
    )


st.markdown("---")

# ========= GRÁFICO 1 — Distribuição de Tipos de Pele por Marca =========
st.markdown("### Distribuição de Tipos de Pele por Marca")

if skin_expl.empty:
    st.info("Sem dados após os filtros.")
else:
    rows = []
    for prod, g in skin_expl.groupby("nome"):
        bases = set()
        for t in g["tipo_pele"]:
            bases.update(to_base_types(t))
        for b in bases:
            rows.append({"produto": prod, "tipo_base": b})
    base_presence = pd.DataFrame(rows)

    available_bases = sorted(base_presence["tipo_base"].dropna().unique().tolist())
    opt_cols = st.columns([1,1,2,2])
    with opt_cols[0]:
        viz = st.radio("Visualização", ["Barras horizontais", "Rosca"],
                       horizontal=False, key="viz_dist", label_visibility="collapsed")
    with opt_cols[1]:
        show_mode = st.radio("Mostrar", ["Todos", "Selecionar"],
                             horizontal=False, key="viz_show", label_visibility="collapsed")
    with opt_cols[2]:
        if show_mode == "Selecionar":
            safe_defaults = [b for b in ["oleosa", "sensível", "todos os tipos"] if b in available_bases][:3]
            sel_bases = st.multiselect("Tipos (quando 'Selecionar')",
                                       options=available_bases,
                                       default=safe_defaults,
                                       key="viz_bases",
                                       label_visibility="collapsed")
        else:
            sel_bases = []
    with opt_cols[3]:
        order_opt = st.radio("Ordenação", ["Quantidade (↓)", "Quantidade (↑)", "Alfabética"],
                             horizontal=True, key="viz_order", label_visibility="collapsed")

    dist = (base_presence.groupby("tipo_base")["produto"].nunique()
            .reset_index(name="produtos"))
    total_prod_scope = base_presence["produto"].nunique()
    dist["pct"] = (dist["produtos"]/max(1,total_prod_scope)*100).round(1)

    if q_skin.strip():
        ql = q_skin.lower()
        dist = dist[dist["tipo_base"].str.contains(ql, na=False)]
    if show_mode == "Selecionar" and sel_bases:
        dist = dist[dist["tipo_base"].isin(sel_bases)]

    if order_opt == "Quantidade (↓)":
        dist = dist.sort_values(["produtos","tipo_base"], ascending=[False, True])
    elif order_opt == "Quantidade (↑)":
        dist = dist.sort_values(["produtos","tipo_base"], ascending=[True, True])
    else:
        if SKIN_TYPE_CANONICAL_ORDER:
            order = [t for t in SKIN_TYPE_CANONICAL_ORDER if t in dist["tipo_base"].unique()]
            dist["tipo_base"] = pd.Categorical(dist["tipo_base"], categories=order, ordered=True)
            dist = dist.sort_values(["tipo_base"])
            dist["tipo_base"] = dist["tipo_base"].astype(str)
        else:
            dist = dist.sort_values("tipo_base")

    title_suffix = "" if sel_cat == "(todas)" else f" • {sel_cat}"

    if dist.empty:
        st.info("Sem dados para exibir a distribuição.")
    else:
        if viz == "Rosca":
            fig = px.pie(
                dist, names="tipo_base", values="produtos",
                hole=0.55, color="tipo_base", color_discrete_sequence=SEQ
            )
            fig.update_traces(
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Produtos: %{value} de " + str(total_prod_scope) + "<br>Participação: %{percent:.1%}<extra></extra>"
            )
            fig.update_layout(
                height=CHART_H,
                legend=dict(font=dict(size=LEGEND_FONT_SIZE, color=text_color())),
                paper_bgcolor=panel_bg(), plot_bgcolor=panel_bg(),
                margin=dict(t=60, b=40, l=10, r=10),
                hoverlabel=dict(font_size=TOOLTIP_FONT_SIZE)
            )
        else:
            base_plot = dist.sort_values("produtos")
            fig = px.bar(
                base_plot, x="produtos", y="tipo_base", orientation="h",
                text="produtos", color="tipo_base", color_discrete_sequence=SEQ,
                labels={"produtos":"Nº de produtos", "tipo_base":""},
                title=f"{sel_brand}{title_suffix}"
            )
            fig.update_traces(
                textposition="outside", textfont=dict(size=BAR_TEXT_SIZE, color="#363636"),
                marker_line_width=.4, marker_line_color="rgba(0,0,0,.12)",
                hovertemplate="<b>%{y}</b><br>Produtos: %{x} de " + str(total_prod_scope) + "<br>Participação: %{customdata[0]}%<extra></extra>",
                customdata=np.expand_dims(base_plot["pct"],1)
            )
            fig.update_layout(
                height=CHART_H, bargap=BARGAP, bargroupgap=BARGROUPGAP,
                showlegend=False, paper_bgcolor=panel_bg(), plot_bgcolor=panel_bg(),
                margin=dict(t=60, b=60, l=10, r=10), hoverlabel=dict(font_size=TOOLTIP_FONT_SIZE)
            )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ========= GRÁFICO 2 — Comparação entre Marcas =========
st.markdown("### Comparação de Tipos de Pele entre Marcas")

col_cmp1, _ = st.columns([2,3])
with col_cmp1:
    marcas_opts = sorted(df["marca"].dropna().unique().tolist())
    sel_marcas_cmp = st.multiselect("Marcas (2–5)",
                                    options=marcas_opts,
                                    default=marcas_opts[:3],
                                    max_selections=5,
                                    key="cmp_brands")
    bases_cmp = st.multiselect("Tipos (opcional)",
                               options=SKIN_TYPE_CANONICAL_ORDER,
                               key="cmp_bases")

if not sel_marcas_cmp:
    st.info("Selecione ao menos uma marca.")
else:
    rows = []
    for mk in sel_marcas_cmp:
        dd = df[df["marca"] == mk].copy()
        if sel_cat != "(todas)":
            dd = dd[dd["categoria"] == sel_cat]
        if dd.empty:
            continue
        ex = explode_skin(dd)
        per_prod = []
        for prod, g in ex.groupby("nome"):
            bases = set()
            for t in g["tipo_pele"]:
                bases.update(to_base_types(t))
            for b in bases:
                per_prod.append({"produto": prod, "tipo_base": b, "marca": mk})
        if per_prod:
            rows.extend(per_prod)
    cmp_df = pd.DataFrame(rows)
    if cmp_df.empty:
        st.info("Sem dados para comparar com os filtros atuais.")
    else:
        dist = (cmp_df.groupby(["tipo_base","marca"])["produto"].nunique().reset_index(name="produtos"))
        if bases_cmp:
            dist = dist[dist["tipo_base"].isin(bases_cmp)]
        order_types = [t for t in SKIN_TYPE_CANONICAL_ORDER if t in dist["tipo_base"].unique()]
        figc = px.bar(
            dist, x="tipo_base", y="produtos", color="marca",
            barmode="group", color_discrete_sequence=SEQ,
            category_orders={"tipo_base": order_types},
            labels={"produtos":"Nº de produtos", "tipo_base":"Tipo de pele"}
        )
        style_axes(figc, height=CHART_H)
        figc.update_layout(legend=dict(font=dict(size=LEGEND_FONT_SIZE)))
        st.plotly_chart(figc, use_container_width=True)

st.markdown("---")

# ========= PESQUISA (lista estilizada) =========
st.markdown("### Pesquisa por Tipo de Pele (lista)")

colp1, colp2, colp3 = st.columns([1.2, 1, 1])
with colp1:
    q = st.text_input("Buscar por tipo (ex.: sensível)", "", key="plist_q")
with colp2:
    brand_p = st.selectbox("Marca", options=["(todas)"] + brands, index=0, key="plist_brand")
with colp3:
    cat_p_opts = ["(todas)"] + sorted(df["categoria"].dropna().unique().tolist())
    if CATEGORY_CANONICAL_ORDER:
        present = [c for c in CATEGORY_CANONICAL_ORDER if c in cat_p_opts]
        cat_p_opts = ["(todas)"] + present + [c for c in cat_p_opts if c not in present and c != "(todas)"]
    cat_p = st.selectbox("Categoria", options=cat_p_opts, index=0, key="plist_cat")

df_p = df.copy()
if brand_p != "(todas)":
    df_p = df_p[df_p["marca"] == brand_p]
if cat_p != "(todas)":
    df_p = df_p[df_p["categoria"] == cat_p]

ex_p = explode_skin(df_p)
if q.strip():
    ql = q.lower()
    ex_p = ex_p[ex_p["tipo_pele"].str.lower().str.contains(ql, na=False)]

def qty_text_row(r: pd.Series) -> str:
    return qty_text(r)

def brl_fmt(x):
    return brl(x)

if ex_p.empty:
    st.info("Nenhum produto encontrado.")
else:
    base_products = (ex_p.groupby("nome")
                        .agg(marca=("marca","first"),
                             categoria=("categoria","first"),
                             preco=("preco","first"),
                             quantidade=("quantidade","first"),
                             quantidade_valor=("quantidade_valor","first"),
                             quantidade_unidade=("quantidade_unidade","first"),
                             tipos=("tipo_pele", lambda s: ", ".join(sorted(set(s)))))
                        .reset_index())

    st.markdown("<div class='list-wrap'>", unsafe_allow_html=True)
    for _, r in base_products.iterrows():
        price = brl_fmt(r.get("preco"))
        qty   = qty_text_row(r)
        tipos_txt = r.get("tipos","—")
        st.markdown(
            f"""
            <div class="row">
              <div class="r-left">
                <div class="name">{r.get('nome','')}</div>
                <div class="brand">{r.get('marca','')}</div>
                <div style="margin-top:6px;"><span class="pill">{r.get('categoria') or "—"}</span></div>
              </div>
              <div>
                <div class="r-price">{price}</div>
                <div class="r-qty">{qty}</div>
              </div>
              <div class="r-mid">
                <div><b>Tipos:</b> {tipos_txt}</div>
              </div>
            </div>
            """, unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

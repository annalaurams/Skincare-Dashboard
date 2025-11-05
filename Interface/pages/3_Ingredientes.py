# pages/3_Ingredientes.py
from __future__ import annotations

# ---- Base centralizada: st, pd, px, load_data, color_sequence, modelos, np, go, Path, re, Optional, List, Tuple etc. ----
from include import *

# ===== Config local só da paleta (NÃO chamar set_page_config/apply_base_theme aqui) =====
if "palette_name" not in st.session_state:
    st.session_state["palette_name"] = "Solaris"

apply_palette_css(st.session_state["palette_name"])

SEQ = color_sequence(st.session_state["palette_name"]) or ["#6e56cf", "#22c55e", "#eab308", "#ef4444", "#06b6d4", "#a855f3"]

# ===== Constantes visuais da página =====
TITLE_TEXT           = "Ingredientes: O que há nas fórmulas"
TAGLINE_TEXT         = "Explore os ingredientes mais presentes e compare a composição entre as marcas"
TITLE_SIZE           = 60
TAGLINE_SIZE         = 26

SECTION_TITLE_SIZE   = 32
SUBTITLE_SIZE        = 22

CHART_HEIGHT         = 680
LEGEND_FONT_SIZE     = 30
TOOLTIP_FONT_SIZE    = 24
AXIS_TITLE_SIZE      = 26
AXIS_TICK_SIZE       = 22
BAR_TEXT_SIZE        = 20
PIE_TEXT_SIZE        = 20

WIDGET_HEIGHT_PX     = 48

def accent(i=0): return SEQ[i % len(SEQ)]
def accent2(): return SEQ[1] if len(SEQ) > 1 else "#22c55e"
def text_color(): return "#262730"
def subtext_color(): return "#555"
def neutral_border(): return "#ebedf0"
def panel_bg(): return "#ffffff"


if "palette_name" not in st.session_state:
    st.session_state["palette_name"] = "Solaris"

apply_base_theme()
apply_palette_css(st.session_state["palette_name"])
SEQ = color_sequence(st.session_state["palette_name"]) or ["#6e56cf", "#22c55e", "#eab308", "#ef4444", "#06b6d4", "#a855f3"]

def accent(i=0): return SEQ[i % len(SEQ)]
def accent2(): return SEQ[1] if len(SEQ) > 1 else "#22c55e"
def text_color(): return "#262730"
def subtext_color(): return "#555"
def neutral_border(): return "#ebedf0"
def panel_bg(): return "#ffffff"

# ===== CSS (mesmo padrão da tela de Benefícios) =====
st.markdown(f"""
<style>
.section-title {{ font-size:{SECTION_TITLE_SIZE}px; font-weight:700; color:{text_color()}; margin: 1rem 0 .5rem 0; }}
.subtle       {{ font-size:{TAGLINE_SIZE}px; color:{subtext_color()}; }}

/* Altura e fonte dos selects/inputs */
.stSelectbox div[role="combobox"],
.stMultiSelect div[role="combobox"],
.stTextInput input, .stTextInput textarea {{
    min-height: {WIDGET_HEIGHT_PX}px !important;
    height: {WIDGET_HEIGHT_PX}px !important;
    font-size: 18px !important;
}}
div[data-baseweb="select"] {{ width: 100% !important; }}

/* Label dos widgets maior */
div[data-testid="stWidgetLabel"] p {{ font-size: 20px !important; }}

/* Opções dos radios maiores */
.stRadio label span {{ font-size: 18px !important; }}

/* Botões de paginação */
.dist-nav .stButton>button {{
    background: {accent(0)}22 !important;
    border: 2px solid {accent(0)} !important;
    color: {text_color()} !important;
    padding: 12px 22px !important;
    height: 52px !important;
    font-size: 19px !important;
    border-radius: 14px !important;
}}

/* NOTA */
.note-box {{
    background: #f8f9fa;
    border: 1px solid {neutral_border()};
    border-left: none;
    padding: 1rem;
    margin: 1rem 0 1.25rem 0;
    border-radius: 10px;
    font-size: 17px;
    line-height: 1.5;
    color: {subtext_color()};
}}
.note-box b {{ color: {text_color()}; }}

/* Cabeçalho de marca */
.brand-header {{
    background: linear-gradient(135deg, {accent(0)} 0%, {accent2()} 100%);
    color: #fff;
    padding: 18px 24px;
    border-radius: 14px;
    font-size: 28px;
    font-weight: 900;
    margin: 32px 0 16px 0;
    box-shadow: 0 4px 12px {accent(0)}40;
}}

/* Tarja de bucket */
.bucket-title {{
    background: {accent(0)}15;
    color: {accent(0)};
    padding: 12px 20px;
    border-radius: 10px;
    font-size: 20px;
    font-weight: 800;
    margin: 16px 0 12px 0;
    border-left: 5px solid {accent(0)};
}}

/* DataFrame */
div[data-testid="stDataFrame"] {{
    border: 1px solid {neutral_border()} !important;
    border-radius: 12px !important;
    overflow: visible !important;
}}
div[data-testid="stDataFrame"] table {{ font-size: 16px !important; line-height: 1.45 !important; }}
div[data-testid="stDataFrame"] thead th {{
    font-size: 18px !important;
    font-weight: 700 !important;
    padding: 10px 14px !important;
    background-color: #fafafa !important;
    color: {text_color()} !important;
    white-space: nowrap !important;
}}
div[data-testid="stDataFrame"] tbody td {{
    padding: 10px 14px !important;
    font-size: 26px !important;
    white-space: normal !important;
    vertical-align: top !important;
}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ===== Ajuste do tamanho da fonte dentro das tabelas ===== */
div[data-testid="stDataFrame"] tbody td div {
    font-size: 42px !important;
    line-height: 1.5 !important;
    white-space: normal !important;
    overflow: visible !important;
}
div[data-testid="stDataFrame"] thead th div {
    font-size: 42px !important;
    font-weight: 700 !important;
}
div[data-testid="stDataFrame"] table {
    border-collapse: separate !important;
    border-spacing: 0 6px !important;
}
</style>
""", unsafe_allow_html=True)

# ===== Helpers =====
def alpha_sorted(opts: List[str]) -> List[str]:
    return sorted([o for o in opts if isinstance(o, str)], key=lambda s: s.casefold())

def _pretty_from_source(fname: str) -> str:
    stem = Path(fname).stem
    for suf in ["_products", "_skincare", "_cosmetics", "_dados"]:
        stem = stem.replace(suf, "")
    return stem.replace("_", " ").title()

def split_semicolon(s: str) -> List[str]:
    if not isinstance(s, str) or not s.strip(): return []
    parts = [p.strip() for chunk in s.split(";") for p in chunk.split(",")]
    return [p for p in parts if p]

def explode_ingredients(df_in: pd.DataFrame) -> pd.DataFrame:
    cols = ["ingrediente","produto","marca","categoria","preco",
            "quantidade_valor","quantidade_unidade","image_url","_source_file"]
    rows = []
    valid = set(INGREDIENTES_VALIDOS) if INGREDIENTES_VALIDOS else None
    if df_in is None or df_in.empty:
        return pd.DataFrame(columns=cols)

    for _, r in df_in.iterrows():
        for ing in split_semicolon(r.get("ingredientes", "")):
            if valid is not None and ing not in valid:
                continue
            rows.append({
                "ingrediente": ing,
                "produto": r.get("nome"),
                "marca": r.get("marca"),
                "categoria": r.get("categoria"),
                "preco": r.get("preco"),
                "quantidade_valor": r.get("quantidade_valor"),
                "quantidade_unidade": r.get("quantidade_unidade"),
                "image_url": r.get("image_url") or r.get("imagem_url") or r.get("imagem"),
                "_source_file": r.get("_source_file"),
            })
    return pd.DataFrame(rows, columns=cols)

def fmt_price(v):
    try:
        x = float(v)
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"

def fmt_qtd(v, u):
    if pd.isna(v): return "—"
    try:
        v_float = float(v)
        v_str = f"{int(v_float)}" if v_float.is_integer() else f"{v_float:.2f}"
    except:
        v_str = str(v)
    return f"{v_str} {u}" if pd.notna(u) and str(u).strip() else v_str

# ===== Carrega dados & opções =====
df = load_data()

uses_files = "_source_file" in df.columns and df["_source_file"].notna().any()
if uses_files:
    files = alpha_sorted(df["_source_file"].dropna().unique().tolist())
    LABEL_MAP = { _pretty_from_source(f): f for f in files }  # label -> arquivo
    BRAND_LABELS = list(LABEL_MAP.keys())
else:
    brands_col = alpha_sorted(df["marca"].dropna().unique().tolist()) if "marca" in df.columns else []
    LABEL_MAP = { b: b for b in brands_col }
    BRAND_LABELS = list(LABEL_MAP.keys())

CAT_ALL  = alpha_sorted(CATEGORY_CANONICAL_ORDER or df.get("categoria", pd.Series(dtype=str)).dropna().unique().tolist())
SKIN_ALL = alpha_sorted(SKIN_TYPE_CANONICAL_ORDER or [])

# ===== Título + Nota =====
st.markdown(f"<h1 style='margin:0; font-size:{TITLE_SIZE}px; color:{accent(0)}'>{TITLE_TEXT}</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='subtle' style='margin:.5rem 0 .75rem 0;'>{TAGLINE_TEXT}</div>", unsafe_allow_html=True)

st.markdown("""
<div class="note-box">
<b>Nota:</b> Este painel utiliza os dados consolidados das marcas brasileiras analisadas.
As contagens consideram <i>produtos distintos</i>. Quando ausentes, algumas informações foram complementadas manualmente.
</div>
""", unsafe_allow_html=True)

# ===== Filtros principais =====
st.markdown(f"<div class='section-title'>Filtros</div>", unsafe_allow_html=True)
fc1, fc2 = st.columns([1.1, 1])
with fc1:
    sel_brand_label = st.selectbox("Marca (obrigatório)", options=BRAND_LABELS, index=0 if BRAND_LABELS else None)
    sel_brand_value = LABEL_MAP.get(sel_brand_label) if sel_brand_label else None
with fc2:
    sel_cat = st.selectbox("Categoria (opcional)", options=["(todas)"] + CAT_ALL, index=0)

if sel_brand_value is None:
    st.info("Selecione uma marca.")
    st.stop()

# Base da marca
df_brand = df[df["_source_file"] == sel_brand_value].copy() if uses_files else df[df["marca"] == sel_brand_label].copy()
if sel_cat != "(todas)":
    df_brand = df_brand[df_brand["categoria"] == sel_cat]

# ===== Resumo =====
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
          <div style="font-weight:400; font-size:28px; color:{text_color()}; line-height:1; margin-top:4px;">
            {value}
          </div>
          <div style="color:{subtext_color()}; margin-top:2px; font-size:18px;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(f"<div class='section-title'>Resumo</div>", unsafe_allow_html=True)

exp_brand = explode_ingredients(df_brand)

if exp_brand.empty:
    top_ing, top_count = "—", 0
else:
    top_s = exp_brand.groupby("ingrediente")["produto"].nunique().sort_values(ascending=False)
    top_ing = top_s.index[0]
    top_count = int(top_s.iloc[0])

exp_all = explode_ingredients(df.copy())
exclusivos = []
if not exp_brand.empty and not exp_all.empty:
    set_marca = set(exp_brand["ingrediente"].unique())
    key = "marca" if "marca" in exp_all.columns else "_source_file"
    by_brand = exp_all.groupby("ingrediente")[key].nunique()
    exclusivos = [b for b in set_marca if by_brand.get(b, 0) == 1]
ex_ing = exclusivos[0] if exclusivos else "—"

kc1, kc2 = st.columns(2)
with kc1:
    summary_card("Ingrediente mais usado", top_ing, f"{top_count} produto(s)", color_idx=1)
with kc2:
    summary_card("Ingrediente exclusivo", ex_ing, "apenas nesta marca (no dataset)", color_idx=2)

st.markdown("---")

# ===== Distribuição de Ingredientes (paginada) =====
st.markdown(f"<div class='section-title'>Distribuição de Ingredientes (paginada)</div>", unsafe_allow_html=True)

if "ing_dist_page" not in st.session_state: st.session_state["ing_dist_page"] = 1

col_sel, col_prev, col_next, _ = st.columns([1.0, 0.6, 0.8, 6])
with col_sel:
    page_size = st.selectbox("Itens por página", options=[10, 15, 20, 25, 30], index=1, key="ing_page_size")
with col_prev:
    st.markdown('<div class="dist-nav">', unsafe_allow_html=True)
    prev = st.button("Anterior", key="ing_prev")
    st.markdown('</div>', unsafe_allow_html=True)
with col_next:
    st.markdown('<div class="dist-nav">', unsafe_allow_html=True)
    next_ = st.button("Próxima", key="ing_next")
    st.markdown('</div>', unsafe_allow_html=True)

if exp_brand.empty:
    st.info("Sem dados para exibir a distribuição.")
else:
    dist = (exp_brand.groupby("ingrediente")["produto"].nunique().reset_index(name="qtd_produtos"))
    dist = dist.sort_values(["qtd_produtos", "ingrediente"], ascending=[False, True]).reset_index(drop=True)

    total_pages = max(1, int(np.ceil(len(dist) / page_size)))
    if prev: st.session_state["ing_dist_page"] = max(1, st.session_state["ing_dist_page"] - 1)
    if next_: st.session_state["ing_dist_page"] = min(total_pages, st.session_state["ing_dist_page"] + 1)

    start = (st.session_state["ing_dist_page"] - 1) * page_size
    end = start + page_size
    page_df = dist.iloc[start:end].copy()

    total_produtos_contexto = df_brand["nome"].nunique() if "nome" in df_brand.columns else 0
    page_df["pct"] = page_df["qtd_produtos"] / float(max(total_produtos_contexto, 1))

    fig = px.bar(
        page_df, x="ingrediente", y="qtd_produtos",
        text="qtd_produtos",
        color="ingrediente", color_discrete_sequence=SEQ,
        labels={"ingrediente": "Ingrediente", "qtd_produtos": "Produtos"}
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=BAR_TEXT_SIZE),
        hovertemplate="<b>%{x}</b><br>Produtos: %{y} de " + str(total_produtos_contexto) +
                      "<br>Participação: %{customdata[0]}<extra></extra>",
        customdata=np.array([[f"{100*p:.1f}%"] for p in page_df["pct"]])
    )
    fig.update_layout(
        height=CHART_HEIGHT,
        showlegend=False,
        bargap=0.12,
        xaxis_tickangle=-20,
        xaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=AXIS_TICK_SIZE)),
        yaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=AXIS_TICK_SIZE)),
        hoverlabel=dict(font_size=TOOLTIP_FONT_SIZE),
        margin=dict(t=40, b=120, l=30, r=20),
        title=f"Página {st.session_state['ing_dist_page']} de {total_pages}"
    )
    st.plotly_chart(fig, width="stretch")

st.markdown("---")

# ===== Top 3 ingredientes da marca =====
st.markdown(f"<div class='section-title'>Top 3 Ingredientes da Marca (todos os produtos)</div>", unsafe_allow_html=True)

df_brand_all = df[df["_source_file"] == sel_brand_value].copy() if uses_files else df[df["marca"] == sel_brand_label].copy()
exp_brand_all = explode_ingredients(df_brand_all)

if exp_brand_all.empty:
    st.info("Sem dados para calcular o Top 3.")
    TOP3_ING = []
else:
    top3 = (exp_brand_all.groupby("ingrediente")["produto"]
            .nunique().sort_values(ascending=False).head(3).reset_index(name="produtos"))
    TOP3_ING = top3["ingrediente"].tolist()
    total_prod = df_brand_all["nome"].nunique()
    top3["pct"] = top3["produtos"] / float(max(total_prod, 1))

    chart_choice = st.radio("Visualização", options=["Barras", "Rosca (%)"], horizontal=True, index=0, key="ing_top_chart")
    if chart_choice == "Barras":
        fig_top = px.bar(
            top3, x="ingrediente", y="produtos", text="produtos",
            color="ingrediente", color_discrete_sequence=SEQ,
            labels={"ingrediente": "Ingrediente", "produtos": "Produtos"}
        )
        fig_top.update_traces(textposition="outside", textfont=dict(size=BAR_TEXT_SIZE))
        fig_top.update_layout(
            height=CHART_HEIGHT//1.2, showlegend=False, bargap=0.12,
            xaxis_tickangle=-20,
            xaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=AXIS_TICK_SIZE)),
            yaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=AXIS_TICK_SIZE)),
            hoverlabel=dict(font_size=TOOLTIP_FONT_SIZE),
            margin=dict(t=40, b=120, l=30, r=20)
        )
    else:
        fig_top = px.pie(
            top3, names="ingrediente", values="pct",
            hole=0.45, color="ingrediente", color_discrete_sequence=SEQ
        )
        fig_top.update_traces(texttemplate="%{label}<br>%{percent:.1%}", textfont_size=PIE_TEXT_SIZE)
        fig_top.update_layout(height=CHART_HEIGHT//1.2, legend=dict(font=dict(size=LEGEND_FONT_SIZE)))
    st.plotly_chart(fig_top, width="stretch")

st.markdown("---")

# ===== Comparação de ingredientes entre marcas (Top 3) =====
st.markdown(f"<div class='section-title'>Comparação de Ingredientes entre Marcas (Top 3)</div>", unsafe_allow_html=True)

brand_opts = ["(todas)"] + BRAND_LABELS
sel_brands = st.multiselect("Marcas", options=brand_opts, default=[sel_brand_label], key="ing_comp_brands")

if "(todas)" in sel_brands:
    sel_brands = BRAND_LABELS[:]
elif not sel_brands:
    sel_brands = [sel_brand_label]

if sel_brands:
    dfs_comp = []
    for lab in sel_brands:
        val = LABEL_MAP[lab]
        base = df[df["_source_file"] == val] if uses_files else df[df["marca"] == lab]
        exp_ = explode_ingredients(base)
        ing_focus = TOP3_ING if 'TOP3_ING' in locals() else []
        if ing_focus:
            exp_ = exp_[exp_["ingrediente"].isin(ing_focus)]
        if exp_.empty:
            local_top = (explode_ingredients(base).groupby("ingrediente")["produto"]
                         .nunique().sort_values(ascending=False).head(3).index.tolist())
            exp_ = explode_ingredients(base)
            exp_ = exp_[exp_["ingrediente"].isin(local_top)]
        grp = (exp_.groupby("ingrediente")["produto"].nunique().reset_index(name="produtos"))
        grp["marca_label"] = lab
        dfs_comp.append(grp)
    comp_df = pd.concat(dfs_comp, ignore_index=True) if dfs_comp else pd.DataFrame()

    if comp_df.empty:
        st.info("Sem dados para comparar.")
    else:
        orient = st.radio("Orientação do gráfico", options=["Barras verticais", "Barras horizontais"], horizontal=True, key="ing_orient")
        if orient == "Barras verticais":
            fig_cmp = px.bar(
                comp_df, x="ingrediente", y="produtos",
                color="marca_label", barmode="group",
                color_discrete_sequence=SEQ,
                labels={"ingrediente": "Ingrediente", "produtos": "Produtos", "marca_label": "Marca"}
            )
        else:
            fig_cmp = px.bar(
                comp_df, x="produtos", y="ingrediente",
                color="marca_label", barmode="group", orientation="h",
                color_discrete_sequence=SEQ,
                labels={"ingrediente": "Ingrediente", "produtos": "Produtos", "marca_label": "Marca"}
            )

        fig_cmp.update_layout(
            height=CHART_HEIGHT,
            bargap=0.12,
            legend=dict(font=dict(size=LEGEND_FONT_SIZE)),
            xaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=AXIS_TICK_SIZE)),
            yaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=AXIS_TICK_SIZE)),
            hoverlabel=dict(font_size=TOOLTIP_FONT_SIZE),
            margin=dict(t=40, b=120, l=30, r=20)
        )
        fig_cmp.update_traces(textfont=dict(size=BAR_TEXT_SIZE))
        st.plotly_chart(fig_cmp, width="stretch")
else:
    st.caption("Selecione ao menos uma marca.")

st.markdown("---")

# ===== Encontrar produtos por ingredientes =====
st.markdown(f"<div class='section-title'>Encontre produtos por ingredientes</div>", unsafe_allow_html=True)
st.markdown("""
<div class="note-box">
<b>Neste modo:</b> Selecione uma ou mais marcas (ou deixe todas), escolha um ou mais ingredientes e, opcionalmente, uma categoria.<br>
Os produtos são organizados em grupos para facilitar a busca:<br>
<b>APENAS: [ingrediente]</b> — produto com SOMENTE aquele ingrediente (entre os válidos/considerados).<br>
<b>EXATAMENTE: [i1 + i2 + ...]</b> — exatamente a combinação selecionada, sem extras (entre os válidos/considerados).<br>
<b>CONTÉM: [ingrediente]</b> — contém o ingrediente, mas também outros.
</div>
""", unsafe_allow_html=True)

brands_all = sorted(df["marca"].dropna().unique().tolist())
sel_brands_search = st.multiselect("Marcas", options=brands_all, default=brands_all, key="tb_brands_ing")

present_ingredients = sorted({i for i in explode_ingredients(df)["ingrediente"].dropna().unique() if i})
ingredient_options = [i for i in INGREDIENTES_VALIDOS if i in present_ingredients] if INGREDIENTES_VALIDOS else present_ingredients
sel_ingredients = st.multiselect(
    "Ingredientes",
    options=ingredient_options,
    default=ingredient_options[:2] if len(ingredient_options) >= 2 else ingredient_options,
    key="tb_ingredients"
)

cats_all_search = sorted(df[df["marca"].isin(sel_brands_search)]["categoria"].dropna().unique().tolist())
if CATEGORY_CANONICAL_ORDER:
    cats_all_search = [c for c in CATEGORY_CANONICAL_ORDER if c in cats_all_search] + [c for c in cats_all_search if c not in CATEGORY_CANONICAL_ORDER]
sel_cat_search = st.selectbox("Categoria (opcional)", options=["(todas)"] + cats_all_search, index=0, key="tb_cat_ing")

if not sel_brands_search or not sel_ingredients:
    st.info("Selecione ao menos uma marca e um ingrediente.")
else:
    base_df_search = df[df["marca"].isin(sel_brands_search)].copy()
    if sel_cat_search != "(todas)":
        base_df_search = base_df_search[base_df_search["categoria"] == sel_cat_search]

    # Agrupar ingredientes por produto
    by_prod_ing = []
    for _, row in base_df_search.iterrows():
        ingr_set = set(split_semicolon(row.get("ingredientes", "")))
        if INGREDIENTES_VALIDOS:
            ingr_set = {i for i in ingr_set if i in INGREDIENTES_VALIDOS}
        by_prod_ing.append({
            "marca": row.get("marca"),
            "nome": row.get("nome"),
            "categoria": row.get("categoria"),
            "beneficios_str": row.get("beneficios", ""),  # mantido na tabela para contexto
            "ingredientes_str": row.get("ingredientes", ""),
            "preco": row.get("preco"),
            "quantidade_valor": row.get("quantidade_valor"),
            "quantidade_unidade": row.get("quantidade_unidade"),
            "bases": ingr_set
        })
    by_prod_df = pd.DataFrame(by_prod_ing)

    if by_prod_df.empty:
        st.info("Sem dados para a seleção atual.")
    else:
        def classify_product_ingredients(bases: set[str], selected: list[str]) -> list[str]:
            buckets = []
            sel_set = set(selected)
            for ing in selected:
                if bases == {ing}:
                    buckets.append(f"APENAS: {ing}")
            if len(sel_set) > 1 and bases == sel_set:
                ing_str = " + ".join(sorted(selected))
                buckets.append(f"EXATAMENTE: {ing_str}")
            for ing in selected:
                if ing in bases and bases != {ing} and bases != sel_set:
                    buckets.append(f"CONTÉM: {ing}")
            return buckets

        bucket_rows = []
        for _, row in by_prod_df.iterrows():
            for bucket in classify_product_ingredients(row["bases"], sel_ingredients):
                d = row.to_dict()
                d["bucket"] = bucket
                bucket_rows.append(d)

        if not bucket_rows:
            st.info("Nenhum produto atende à seleção.")
        else:
            by_prod_exploded = pd.DataFrame(bucket_rows)

            bucket_order = []
            if len(sel_ingredients) > 1:
                bucket_order.append("EXATAMENTE: " + " + ".join(sorted(sel_ingredients)))
            for i in sel_ingredients:
                bucket_order.append(f"APENAS: {i}")
            for i in sel_ingredients:
                bucket_order.append(f"CONTÉM: {i}")

            # Tabelas por marca
            for marca in sel_brands_search:
                sub = by_prod_exploded[by_prod_exploded["marca"] == marca]
                if sub.empty:
                    continue

                st.markdown(f"<div class='brand-header'>{marca}</div>", unsafe_allow_html=True)

                for bucket in bucket_order:
                    tb = sub[sub["bucket"] == bucket].copy()
                    if tb.empty:
                        continue

                    st.markdown(f"<div class='bucket-title'>{bucket}</div>", unsafe_allow_html=True)

                    tb["Preço"] = tb["preco"].apply(fmt_price)
                    tb["Quantidade"] = tb.apply(lambda r: fmt_qtd(r["quantidade_valor"], r["quantidade_unidade"]), axis=1)

                    display_tb = tb[["nome","categoria","Quantidade","Preço","ingredientes_str","beneficios_str"]].rename(columns={
                        "nome": "Produto",
                        "categoria": "Categoria",
                        "ingredientes_str": "Ingredientes",
                        "beneficios_str": "Benefícios"
                    }).fillna("—").drop_duplicates()

                    st.dataframe(display_tb, width="stretch", hide_index=True)

            # Gráficos após as tabelas
            st.markdown("---")
            st.markdown("### Visualizações resumidas da sua seleção")
            st.markdown("""
<div class="note-box">
<b>O que você vê aqui?</b><br>
• <b>Por marca × bucket</b>: quantos produtos de cada marca caíram em cada grupo mostrado nas tabelas (empilhado ou agrupado).
</div>
""", unsafe_allow_html=True)

            agg_bucket = (
                by_prod_exploded
                .groupby(["marca","bucket"])["nome"]
                .nunique()
                .reset_index(name="produtos")
            )
            agg_bucket["bucket"] = pd.Categorical(agg_bucket["bucket"], categories=bucket_order, ordered=True)
            agg_bucket = agg_bucket.sort_values(["bucket","marca"])

            bar_mode = st.radio("Modo", ["Empilhado", "Agrupado"], horizontal=True, key="g_sum_mode_ing")
            barmode = "stack" if bar_mode == "Empilhado" else "group"

            fig_sum = px.bar(
                agg_bucket, x="marca", y="produtos", color="bucket", barmode=barmode,
                color_discrete_sequence=SEQ,
                labels={"marca":"Marca", "produtos":"Nº de produtos", "bucket":"Grupo"},
            )
            fig_sum.update_traces(
                hovertemplate="<b>%{x}</b><br>Grupo: <b>%{fullData.name}</b><br>Produtos: <b>%{y}</b><extra></extra>"
            )
            fig_sum.update_layout(
                height=720,
                margin=dict(t=40, b=80, l=20, r=260),
                legend=dict(font=dict(size=LEGEND_FONT_SIZE), itemwidth=90),
                xaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=AXIS_TICK_SIZE)),
                yaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=AXIS_TICK_SIZE)),
                hoverlabel=dict(font_size=TOOLTIP_FONT_SIZE)
            )
            st.plotly_chart(fig_sum, width="stretch")

st.markdown("---")

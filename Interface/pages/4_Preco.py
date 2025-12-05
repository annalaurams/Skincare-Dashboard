from __future__ import annotations
from include import * 
from core.data import load_data  

if "palette_name" not in st.session_state:
    st.session_state["palette_name"] = "Solaris"

st.set_page_config(page_title="Preço", page_icon="", layout="wide")
apply_base_theme()
apply_palette_css(st.session_state["palette_name"])
SEQ = color_sequence(st.session_state["palette_name"]) or ["#6e56cf", "#22c55e", "#eab308", "#ef4444", "#06b6d4", "#a855f7"]

def accent(i=0): return SEQ[i % len(SEQ)]
def text_color(): return "#262730"
def subtext_color(): return "#555"
def panel_bg(): return "#ffffff"

TITLE_TEXT   = "Panorama de Preços"
TAGLINE_TEXT = "Veja preços, variações por marca, categoria, ingredientes, benefícios e tipos de pele."
TITLE_SIZE, TAGLINE_SIZE = 60, 24
AXIS_TITLE_SIZE, AXIS_TICK_SIZE = 22, 22
LEGEND_FONT_SIZE = 26
CHART_HEIGHT = 640
SCATTER_MARKER_SIZE = 22

# HELPERS
def _pretty_from_source(fname: str) -> str:
    stem = Path(fname).stem
    for suf in ["_products", "_skincare", "_cosmetics", "_dados"]:
        stem = stem.replace(suf, "")
    return stem.replace("_", " ").title()

def brl(x) -> str:
    if x is None or pd.isna(x): return "—"
    return f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def split_semicolon(s: str):
    if not isinstance(s, str) or not s.strip():
        return []
    return [p.strip() for p in s.split(";") if p.strip()]

def style_axes(fig, height=CHART_HEIGHT):
    fig.update_layout(
        height=height,
        paper_bgcolor=panel_bg(),
        plot_bgcolor=panel_bg(),
        font=dict(size=AXIS_TICK_SIZE, color=text_color()),
        xaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=AXIS_TICK_SIZE), gridcolor="rgba(0,0,0,.08)"),
        yaxis=dict(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=AXIS_TICK_SIZE), gridcolor="rgba(0,0,0,.08)"),
        legend=dict(font=dict(size=LEGEND_FONT_SIZE)),
        hoverlabel=dict(font_size=18),
        margin=dict(t=60, b=70, l=30, r=20),
        modebar=dict(remove=['zoom', 'pan', 'select', 'lasso2d', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale'])
    )
    return fig

def order_by_canonical(series: pd.Series, canonical: List[str]) -> List[str]:
    uniq = series.dropna().astype(str).unique().tolist()
    if not canonical: return sorted(uniq)
    ordered = [c for c in canonical if c in uniq]
    for x in uniq:
        if x not in ordered:
            ordered.append(x)
    return ordered

def format_quantidade(valor, unidade):
    """Formata a quantidade de forma legível"""
    if pd.isna(valor) and pd.isna(unidade):
        return "—"
    
    valor_str = ""
    if not pd.isna(valor):
        try:
            v = float(valor)
            valor_str = f"{int(v)}" if v.is_integer() else f"{v:.2f}"
        except:
            valor_str = str(valor)
    
    unidade_str = str(unidade) if not pd.isna(unidade) else ""
    
    if valor_str and unidade_str:
        return f"{valor_str} {unidade_str}"
    elif valor_str:
        return valor_str
    elif unidade_str:
        return unidade_str
    else:
        return "—"

# =============================
# DADOS – usa o mesmo loader do app
# =============================

df_all = load_data().copy()

# garante colunas esperadas
for col in ["nome", "marca", "categoria", "tipo_pele", "beneficios", "ingredientes", "preco",
            "quantidade_valor", "quantidade_unidade"]:
    if col not in df_all.columns:
        df_all[col] = pd.NA

# se não tiver _source_file (marca vinda de CSV), usa a própria marca
if "_source_file" not in df_all.columns:
    df_all["_source_file"] = df_all["marca"].astype(str)

df_all["__brand_label__"] = df_all["_source_file"].map(_pretty_from_source)
BRAND_COL = "__brand_label__"
BRAND_LABELS = sorted(df_all[BRAND_COL].dropna().unique().tolist())

CAT_LIST = CATEGORY_CANONICAL_ORDER[:] if CATEGORY_CANONICAL_ORDER else \
           sorted(df_all["categoria"].dropna().unique().tolist())

# normaliza textos
for c in ["nome", "marca", "categoria", "tipo_pele", "beneficios", "ingredientes"]:
    df_all[c] = df_all[c].astype(str).str.strip()

# Cria coluna formatada de quantidade para exibição
df_all["quantidade_formatada"] = df_all.apply(
    lambda r: format_quantidade(r.get("quantidade_valor"), r.get("quantidade_unidade")), 
    axis=1
)

# ==========================
# explode_dimension ROBUSTA
# ==========================
def explode_dimension(
    df_in: pd.DataFrame,
    col: str,
    target_name: str,
    whitelist: Optional[List[str]] = None,
    brand_col: str = BRAND_COL
) -> pd.DataFrame:
    rows = []
    allowed = set(whitelist) if whitelist else None

    for _, r in df_in.iterrows():
        items = split_semicolon(r.get(col, ""))
        for item in items:
            if allowed is not None and item not in allowed:
                continue
            rows.append({
                target_name: item,
                "preco": r.get("preco"),
                "produto": r.get("nome"),
                "marca": r.get("marca"),
                brand_col: r.get(brand_col),
                "categoria": r.get("categoria"),
                "beneficios": r.get("beneficios"),
                "ingredientes": r.get("ingredientes"),
                "tipo_pele": r.get("tipo_pele"),
                "quantidade_formatada": r.get("quantidade_formatada"),
            })

    df_out = pd.DataFrame(rows)

    # garante as colunas mesmo se não houver linhas (evita KeyError)
    if df_out.empty:
        df_out = pd.DataFrame(columns=[
            target_name,
            "preco", "produto", "marca", brand_col,
            "categoria", "beneficios", "ingredientes",
            "tipo_pele", "quantidade_formatada"
        ])

    return df_out

# HEADER
st.markdown(f"<h1 style='margin:0; font-size:{TITLE_SIZE}px; color:{accent(0)}'>{TITLE_TEXT}</h1>", unsafe_allow_html=True)
st.markdown(f"<div style='margin:.25rem 0 1rem 0; color:{subtext_color()}; font-size:{TAGLINE_SIZE}px'>{TAGLINE_TEXT}</div>", unsafe_allow_html=True)

# 📝 NOTA SIMPLES 
st.markdown("""
<style>
.simple-note {
  background: rgba(0,0,0,0.03);
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 16px;
  color: #444;
  line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)
st.markdown(
    "<div class='simple-note'>"
    "Este painel consolida dados coletados nos sites oficiais das marcas brasileiras analisadas."
    "<br>Selecione <b>uma marca</b> e, opcionalmente, <b>uma categoria</b> para filtrar os resultados."
    "<br>Com esses filtros, você verá os <b>KPIs</b>: total de produtos da seleção, <b>marca</b>, <b>preço médio</b>, <b>mínimo</b> e <b>máximo</b>."
    "<br>Também exibimos os <b>3 produtos mais caros</b> e os <b>3 mais baratos</b> com base nos filtros aplicados."
    "</div>",
    unsafe_allow_html=True
)

# (estilos dos cards — mantidos)
st.markdown(f"""
<style>
.cardgrid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(480px, 1fr)); gap: 20px; margin-bottom: 20px; }}
.card {{ background: linear-gradient(135deg, #ffffff 0%, #f8f9fc 100%); border-radius: 22px; padding: 24px 28px; border: 2px solid {accent(0)}40; box-shadow: 0 4px 12px rgba(0,0,0,.06); display: flex; flex-direction: column; justify-content: space-between; min-height: 140px; height: 100%; }}
.card .content {{ display: flex; justify-content: space-between; align-items: center; gap: 20px; flex: 1; }}
.card .left {{ flex: 1; min-width: 0; }}
.card .left .title {{ font-size: 22px; font-weight: 700; color: {text_color()}; margin: 0; line-height: 1.4; word-wrap: break-word; }}
.card .left .subtitle {{ font-size: 20px; color: {subtext_color()}; margin-top: 12px; font-weight: 600; line-height: 1.3; }}
.badge {{ display: inline-block; padding: 6px 14px; border-radius: 999px; font-size: 13px; font-weight: 700; color: #fff; margin-top: 8px; white-space: nowrap; }}
.badge.caro {{ background: linear-gradient(135deg, {accent(3)} 0%, {SEQ[(3+1) % len(SEQ)]} 100%); }}
.badge.barato {{ background: linear-gradient(135deg, {accent(1)} 0%, {SEQ[(1+1) % len(SEQ)]} 100%); }}
.price {{ font-size: 38px; color: {accent(0)}; font-weight: 900; text-align: right; white-space: nowrap; flex-shrink: 0; }}
.kpi-box {{ border: 4px solid {accent(0)}; border-radius: 22px; padding: 26px; background: linear-gradient(135deg, #ffffff 0%, {accent(0)}10 100%); text-align: center; height: 170px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,.06); }}
.kpi-title {{ font-size: 22px; font-weight: 700; color: {subtext_color()}; }}
.kpi-value {{ font-size: 40px; font-weight: 800; color: {accent(0)}; margin-top: .5rem; }}
.sectioncap {{ font-size: 20px; font-weight: 700; color: {text_color()}; margin: .75rem 0 1rem; }}
.details-table {{ width: 100%; border-collapse: collapse; margin-top: 1.2rem; background: {panel_bg()}; border-radius: 18px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
.details-table thead {{ background: linear-gradient(135deg, {accent(0)} 0%, {accent(1)} 100%); color: white; }}
.details-table th {{ padding: 18px 20px; text-align: left; font-weight: 700; font-size: 18px; border-bottom: 3px solid rgba(255,255,255,.2); }}
.details-table td {{ padding: 16px 20px; font-size: 17px; color: {text_color()}; border-bottom: 1px solid #f0f0f5; }}
.details-table tbody tr:hover {{ background: linear-gradient(90deg, {accent(0)}0D 0%, transparent 100%); }}
.details-table tbody tr:last-child td {{ border-bottom: none; }}
.brand-caption {{ margin-top: 18px; margin-bottom: 6px; font-weight: 900; font-size: 22px; color: #fff; padding: 8px 14px; border-radius: 14px; background: linear-gradient(90deg, {accent(4)} 0%, {accent(2)} 100%); }}
.radio-container {{ background: {panel_bg()}; padding: 18px 24px; border-radius: 18px; border: 2px solid {accent(0)}33; margin: 1rem 0; }}
.radio-container label {{ font-size: 20px !important; font-weight: 700 !important; color: {text_color()} !important; }}
.stRadio > div[role='radiogroup'] > label p {{ font-size: 20px !important; }}
</style>
""", unsafe_allow_html=True)

# FILTROS INICIAIS
st.markdown(f"<div style='font-size:32px; font-weight:800; color:{accent(0)}; margin:1.2rem 0 1rem 0;'>Filtros Iniciais</div>", unsafe_allow_html=True)
fc1, fc2 = st.columns([1.1, 1])
with fc1:
    sel_brand_label = st.selectbox("Marca (obrigatório)", options=BRAND_LABELS, index=0, key="f_brand")
with fc2:
    sel_cat = st.selectbox("Categoria (opcional)", options=["(todas)"] + CAT_LIST, index=0, key="f_cat")

df_kpi = df_all[df_all[BRAND_COL] == sel_brand_label].copy()
if sel_cat != "(todas)":
    df_kpi = df_kpi[df_kpi["categoria"] == sel_cat]

# KPIs
k1, k2, k3, k4 = st.columns(4)
total_prod = len(df_kpi)
preco_med  = df_kpi["preco"].mean() if not df_kpi.empty else np.nan
preco_min  = df_kpi["preco"].min()  if not df_kpi.empty else np.nan
preco_max  = df_kpi["preco"].max()  if not df_kpi.empty else np.nan

def kpi_box(title, value, color_idx):
    st.markdown(
        f"""
        <div class="kpi-box" style="border-color:{accent(color_idx)}; background: linear-gradient(135deg, #ffffff 0%, {accent(color_idx)}12 100%);">
          <div class="kpi-title">{title}</div>
          <div class="kpi-value" style="color:{accent(color_idx)}">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with k1: kpi_box("Total de produtos", str(total_prod), 0)
with k2: kpi_box("Preço médio", brl(preco_med), 1)
with k3: kpi_box("Preço mínimo", brl(preco_min), 2)
with k4: kpi_box("Preço máximo", brl(preco_max), 3)

# CARDS: TOP 3 CAROS/BARATOS
st.markdown(f"<div style='font-size:32px; font-weight:800; color:{accent(1)}; margin:2rem 0 1rem 0;'>Produtos mais caros e mais baratos</div>", unsafe_allow_html=True)

def _render_card(prod, tipo):
    nome = prod.get("nome","—")
    cat  = prod.get("categoria","—")
    preco = brl(prod.get("preco"))
    qtd = prod.get("quantidade_formatada", "—")
    badge_class = "caro" if tipo=="Mais caro" else "barato"
    badge_text  = "Mais caro" if tipo=="Mais caro" else "Mais barato"
    return f"""
      <div class="card">
        <div class="content">
          <div class="left">
            <p class="title">{nome}</p>
            <p class="subtitle">{cat} • {qtd}</p>
            <span class="badge {badge_class}">{badge_text}</span>
          </div>
          <div class="price">{preco}</div>
        </div>
      </div>
    """

base_brand = df_all[df_all[BRAND_COL] == sel_brand_label].copy()
if sel_cat != "(todas)":
    base_brand = base_brand[base_brand["categoria"] == sel_cat]

left, right = st.columns(2)
with left:
    st.markdown(f"<div class='sectioncap'>Top 3 mais caros — {sel_brand_label}{'' if sel_cat=='(todas)' else ' • ' + sel_cat}</div>", unsafe_allow_html=True)
    if base_brand.empty:
        st.info("Sem produtos para a seleção.")
    else:
        top3_caro = base_brand.sort_values("preco", ascending=False).head(3)
        st.markdown("<div class='cardgrid'>", unsafe_allow_html=True)
        for _, r in top3_caro.iterrows():
            st.markdown(_render_card(r, "Mais caro"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown(f"<div class='sectioncap'>Top 3 mais baratos — {sel_brand_label}{'' if sel_cat=='(todas)' else ' • ' + sel_cat}</div>", unsafe_allow_html=True)
    if base_brand.empty:
        st.info("Sem produtos para a seleção.")
    else:
        top3_barato = base_brand.sort_values("preco", ascending=True).head(3)
        st.markdown("<div class='cardgrid'>", unsafe_allow_html=True)
        for _, r in top3_barato.iterrows():
            st.markdown(_render_card(r, "Mais barato"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

st.markdown(
    f"<div style='font-size:32px; font-weight:800; color:{accent(2)}; margin:2rem 0 1rem 0;'>Padrões de Quantidade</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='simple-note'>"
    "<b>Nota:</b> A análise da quantidade dos produtos é apresentada de forma descritiva, "
    "sem conversões entre unidades de massa (g) e volume (mL)."
    "</div>",
    unsafe_allow_html=True
)

# Análise descritiva das quantidades
df_qtd_analise = df_all[df_all[BRAND_COL] == sel_brand_label].copy()
if sel_cat != "(todas)":
    df_qtd_analise = df_qtd_analise[df_qtd_analise["categoria"] == sel_cat]

# Conta distribuição de unidades
df_qtd_validas = df_qtd_analise[df_qtd_analise["quantidade_unidade"].notna()].copy()

if not df_qtd_validas.empty:
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    # Unidades mais comuns
    unidades_count = df_qtd_validas["quantidade_unidade"].value_counts()
    
    with col_stat1:
        st.markdown(
            f"""
            <div class="kpi-box" style="border-color:{accent(0)}; background: linear-gradient(135deg, #ffffff 0%, {accent(0)}12 100%);">
              <div class="kpi-title">Unidade mais comum</div>
              <div class="kpi-value" style="color:{accent(0)}">{unidades_count.index[0] if len(unidades_count) > 0 else '—'}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col_stat2:
        produtos_com_qtd = len(df_qtd_validas)
        total_produtos = len(df_qtd_analise)
        percentual = (produtos_com_qtd / total_produtos * 100) if total_produtos > 0 else 0
        
        st.markdown(
            f"""
            <div class="kpi-box" style="border-color:{accent(1)}; background: linear-gradient(135deg, #ffffff 0%, {accent(1)}12 100%);">
              <div class="kpi-title">Produtos com quantidade informada</div>
              <div class="kpi-value" style="color:{accent(1)}">{produtos_com_qtd}/{total_produtos} ({percentual:.0f}%)</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col_stat3:
        # Variedade de tamanhos
        tamanhos_unicos = df_qtd_validas["quantidade_formatada"].nunique()
        
        st.markdown(
            f"""
            <div class="kpi-box" style="border-color:{accent(2)}; background: linear-gradient(135deg, #ffffff 0%, {accent(2)}12 100%);">
              <div class="kpi-title">Variedade de tamanhos</div>
              <div class="kpi-value" style="color:{accent(2)}">{tamanhos_unicos}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

else:
    st.info("Não há informações de quantidade disponíveis para a seleção atual.")

st.markdown("---")

# UTIL: agregação min/méd/máx
def agg_min_med_max(df: pd.DataFrame, by: List[str]) -> pd.DataFrame:
    g = df.groupby(by, dropna=False)["preco"].agg(['min','mean','max','count']).reset_index()
    g.rename(columns={"min":"preco_min","mean":"preco_med","max":"preco_max","count":"n_produtos"}, inplace=True)
    return g

# 📋 tabela com subtítulo por marca 
def render_details_table_products_grouped_by_brand(df: pd.DataFrame, extra_cols: List[str], brand_col: str = BRAND_COL):
    base_cols = ["nome","categoria","quantidade_formatada","preco"]
    all_cols = [c for c in (base_cols + extra_cols) if c in df.columns]
    
    for brand, sub in df.sort_values([brand_col, "categoria","nome"]).groupby(brand_col):
        st.markdown(f"<div class='brand-caption'>{brand}</div>", unsafe_allow_html=True)
        show = sub[all_cols].copy()
        
        headers_map = {
            "nome":"Produto",
            "categoria":"Categoria",
            "quantidade_formatada":"Quantidade",
            "preco":"Preço",
            "ingredientes":"Ingredientes",
            "beneficios":"Benefícios",
            "tipo_pele":"Tipos de pele"
        }
        
        thead = "".join([f"<th>{headers_map.get(c, c.title())}</th>" for c in all_cols])
        rows_html = []
        
        for _, r in show.iterrows():
            tds = []
            for c in all_cols:
                v = r[c]
                if c == "preco":
                    tds.append(f"<td>{brl(v)}</td>")
                else:
                    tds.append(f"<td>{'-' if pd.isna(v) else str(v)}</td>")
            rows_html.append("<tr>" + "".join(tds) + "</tr>")
        
        html = f"<table class='details-table'><thead><tr>{thead}</tr></thead><tbody>{''.join(rows_html)}</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)

# 📄 Paginação 
def paginate(df: pd.DataFrame, key_base: str, page_size: int) -> Tuple[pd.DataFrame, int, int]:
    total = len(df)
    idx_key = f"{key_base}_idx"
    if idx_key not in st.session_state: st.session_state[idx_key] = 0
    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("⟵ Anterior", disabled=st.session_state[idx_key] == 0, key=f"{key_base}_prev"):
            st.session_state[idx_key] = max(0, st.session_state[idx_key] - page_size)
    with c2:
        if st.button("Próximo ⟶", disabled=(st.session_state[idx_key] + page_size >= total), key=f"{key_base}_next"):
            st.session_state[idx_key] = min(total-1, st.session_state[idx_key] + page_size)
    start = st.session_state[idx_key]
    end = min(total, start + page_size)
    st.caption(f"Mostrando {start+1}–{end} de {total}")
    return df.iloc[start:end], start, end

# ANÁLISES COMPARATIVAS
st.markdown(f"<div style='font-size:32px; font-weight:800; color:{accent(3)}; margin:2rem 0 1rem 0;'>Análises Comparativas</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sectioncap'>Escolha o fluxo de análise</div>", unsafe_allow_html=True)

analysis_mode = st.radio("Fluxo", ["Fixar uma marca", "Comparar marcas"], horizontal=True, key="analysis_mode")

if analysis_mode == "Fixar uma marca":
    col_a1, col_a2, col_a3 = st.columns([1.2, 1, 0.8])
    with col_a1:
        brand_A = st.selectbox("Marca", options=BRAND_LABELS, index=BRAND_LABELS.index(sel_brand_label) if sel_brand_label in BRAND_LABELS else 0, key="brand_A")
    with col_a2:
        facet_A = st.selectbox("Dimensão", options=["Categoria","Ingrediente","Benefício","Tipo de pele"], index=0, key="facet_A")
    with col_a3:
        page_size_A = st.selectbox("Itens por página", options=[2,4,6,8,10], index=2, key="page_size_A")

    base_A = df_all[df_all[BRAND_COL] == brand_A].copy()

    if facet_A == "Categoria":
        agg_df = agg_min_med_max(base_A.dropna(subset=["categoria","preco"]), ["categoria"])
        dim_col = "categoria"; canonical = CATEGORY_CANONICAL_ORDER
        details_df = base_A.dropna(subset=["preco"])
    elif facet_A == "Ingrediente":
        exp = explode_dimension(base_A, "ingredientes", "ingrediente", whitelist=INGREDIENTES_VALIDOS)
        agg_df = agg_min_med_max(exp.dropna(subset=["ingrediente","preco"]), ["ingrediente"])
        dim_col, canonical = "ingrediente", INGREDIENTES_VALIDOS
        details_df = base_A.merge(exp[["produto","ingrediente"]].drop_duplicates(), how="left", left_on="nome", right_on="produto").drop(columns=["produto"])
    elif facet_A == "Benefício":
        exp = explode_dimension(base_A, "beneficios", "beneficio", whitelist=BENEFIT_CANONICAL_ORDER)
        agg_df = agg_min_med_max(exp.dropna(subset=["beneficio","preco"]), ["beneficio"])
        dim_col, canonical = "beneficio", BENEFIT_CANONICAL_ORDER
        details_df = base_A.merge(exp[["produto","beneficio"]].drop_duplicates(), how="left", left_on="nome", right_on="produto").drop(columns=["produto"])
    else:
        exp = explode_dimension(base_A, "tipo_pele", "tipo_pele", whitelist=SKIN_TYPE_CANONICAL_ORDER)
        agg_df = agg_min_med_max(exp.dropna(subset=["tipo_pele","preco"]), ["tipo_pele"])
        dim_col, canonical = "tipo_pele", SKIN_TYPE_CANONICAL_ORDER
        details_df = base_A.merge(exp[["produto","tipo_pele"]].drop_duplicates(), how="left", left_on="nome", right_on="produto").drop(columns=["produto"])

    if agg_df.empty:
        st.info("Sem dados para essa combinação.")
    else:
        order = order_by_canonical(agg_df[dim_col].astype(str), canonical)
        agg_df[dim_col] = pd.Categorical(agg_df[dim_col], categories=order, ordered=True)
        agg_df = agg_df.sort_values(dim_col)

        agg_page, _s, _e = paginate(agg_df, key_base=f"fix_brand_{facet_A}", page_size=page_size_A)

        figA = go.Figure()
        figA.add_bar(
            name="Preço médio", x=agg_page[dim_col], y=agg_page["preco_med"],
            marker_color=accent(0),
            customdata=np.stack([agg_page["n_produtos"].values, agg_page["preco_min"].values, agg_page["preco_max"].values], axis=-1),
            hovertemplate="<b>%{x}</b><br>Médio: R$ %{y:.2f}<br>Mín: R$ %{customdata[1]:.2f}<br>Máx: R$ %{customdata[2]:.2f}<br>N: %{customdata[0]}<extra></extra>"
        )
        figA.add_scatter(
            name="Mínimo", x=agg_page[dim_col], y=agg_page["preco_min"],
            mode="markers", marker_symbol="diamond", marker_size=16, marker_color=accent(2),
            hovertemplate="<b>%{x}</b><br>Mínimo: R$ %{y:.2f}<extra></extra>"
        )
        figA.add_scatter(
            name="Máximo", x=agg_page[dim_col], y=agg_page["preco_max"],
            mode="markers", marker_symbol="diamond", marker_size=16, marker_color=accent(4),
            hovertemplate="<b>%{x}</b><br>Máximo: R$ %{y:.2f}<extra></extra>"
        )
        figA.update_layout(xaxis_title=facet_A, yaxis_title="Preço (R$)")
        figA.update_yaxes(range=[0,150])
        style_axes(figA, height=CHART_HEIGHT)
        figA.update_xaxes(tickangle=30)
        st.plotly_chart(figA, use_container_width=True, config={'displayModeBar': False})

        st.markdown(
            "<div class='simple-note'>"
            "<b>Nota:</b> Gráfico que evidencia os preços médio, mínimo e máximo dos produtos de acordo com os filtros escolhidos"
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown(f"<div class='sectioncap'>Ver detalhes — {brand_A} por {facet_A.lower()}</div>", unsafe_allow_html=True)
        extra = st.multiselect("Colunas extras para ver nos detalhes", options=["ingredientes","beneficios","tipo_pele"], default=[], key=f"extra_cols_fix_{facet_A}")
        tmp = details_df.copy(); tmp[BRAND_COL] = brand_A
        render_details_table_products_grouped_by_brand(tmp, extra_cols=extra, brand_col=BRAND_COL)

else:
    col_b1, col_b2, col_b3 = st.columns([1.2, 1, 0.8])
    with col_b1:
        facet_B = st.selectbox("Fixar um item de…", options=["Categoria","Ingrediente","Benefício","Tipo de pele"], index=0, key="facet_B")
    with col_b2:
        if facet_B == "Categoria":
            values = CATEGORY_CANONICAL_ORDER[:] if CATEGORY_CANONICAL_ORDER else sorted(df_all["categoria"].dropna().unique().tolist())
            label_B = st.selectbox("Escolha a categoria", options=values, key="label_B_cat")
            base_B = df_all[df_all["categoria"] == label_B].copy()
        elif facet_B == "Ingrediente":
            exp_all = explode_dimension(df_all, "ingredientes", "ingrediente", whitelist=INGREDIENTES_VALIDOS)
            if exp_all.empty:
                st.info("Sem dados de ingredientes para essa combinação.")
                base_B = exp_all.iloc[0:0]
            else:
                values = INGREDIENTES_VALIDOS[:] if INGREDIENTES_VALIDOS else sorted(
                    exp_all["ingrediente"].dropna().unique().tolist()
                )
                label_B = st.selectbox("Escolha o ingrediente", options=values, key="label_B_ing")
                base_B = exp_all[exp_all["ingrediente"] == label_B].copy()
        elif facet_B == "Benefício":
            exp_all = explode_dimension(df_all, "beneficios", "beneficio", whitelist=BENEFIT_CANONICAL_ORDER)
            values = BENEFIT_CANONICAL_ORDER[:] if BENEFIT_CANONICAL_ORDER else sorted(exp_all["beneficio"].dropna().unique().tolist())
            label_B = st.selectbox("Escolha o benefício", options=values, key="label_B_ben")
            base_B = exp_all[exp_all["beneficio"] == label_B].copy()
        else:
            exp_all = explode_dimension(df_all, "tipo_pele", "tipo_pele", whitelist=SKIN_TYPE_CANONICAL_ORDER)
            values = SKIN_TYPE_CANONICAL_ORDER[:] if SKIN_TYPE_CANONICAL_ORDER else sorted(exp_all["tipo_pele"].dropna().unique().tolist())
            label_B = st.selectbox("Escolha o tipo de pele", options=values, key="label_B_skin")
            base_B = exp_all[exp_all["tipo_pele"] == label_B].copy()
    with col_b3:
        page_size_B = st.selectbox("Itens por página", options=[2,4,6,8,10], index=2, key="page_size_B")

    ms_brands = st.multiselect("Marcas para comparar", options=BRAND_LABELS, default=BRAND_LABELS, key="brands_B")
    if ms_brands:
        base_B = base_B[base_B[BRAND_COL].isin(ms_brands)]
    else:
        base_B = base_B.iloc[0:0]

    if base_B.empty:
        st.info("Sem dados para essa combinação.")
    else:
        aggB = agg_min_med_max(base_B.dropna(subset=["preco"]), [BRAND_COL]).rename(columns={BRAND_COL:"Marca"})
        aggB = aggB.sort_values("preco_med")

        aggB_page, _s, _e = paginate(aggB, key_base=f"cmp_brands_{facet_B}", page_size=page_size_B)

        figB = go.Figure()
        figB.add_bar(
            name="Preço médio", x=aggB_page["Marca"], y=aggB_page["preco_med"],
            marker_color=accent(0),
            customdata=np.stack([aggB_page["n_produtos"].values, aggB_page["preco_min"].values, aggB_page["preco_max"].values], axis=-1),
            hovertemplate="<b>%{x}</b><br>Médio: R$ %{y:.2f}<br>Mín: R$ %{customdata[1]:.2f}<br>Máx: R$ %{customdata[2]:.2f}<br>N: %{customdata[0]}<extra></extra>"
        )
        figB.add_scatter(
            name="Mínimo", x=aggB_page["Marca"], y=aggB_page["preco_min"],
            mode="markers", marker_symbol="diamond", marker_size=16, marker_color=accent(2),
            hovertemplate="<b>%{x}</b><br>Mínimo: R$ %{y:.2f}<extra></extra>"
        )
        figB.add_scatter(
            name="Máximo", x=aggB_page["Marca"], y=aggB_page["preco_max"],
            mode="markers", marker_symbol="diamond", marker_size=16, marker_color=accent(4),
            hovertemplate="<b>%{x}</b><br>Máximo: R$ %{y:.2f}<extra></extra>"
        )
        figB.update_layout(xaxis_title="Marca", yaxis_title="Preço (R$)")
        figB.update_yaxes(range=[0,150])
        style_axes(figB, height=CHART_HEIGHT)
        figB.update_xaxes(tickangle=30)
        st.plotly_chart(figB, use_container_width=True, config={'displayModeBar': False})

        st.markdown(
            f"<div class='simple-note'>Comparação por <b>{facet_B}</b>: {label_B}. <br> A barra mostra o <b>médio</b> e os losangos, <b>mínimo</b> e <b>máximo</b>. <br> O tooltip inclui o <b>N de produtos</b>. Preço fixo em 0–150.</div>",
            unsafe_allow_html=True
        )

        st.markdown(f"<div class='sectioncap'>Ver detalhes — {facet_B}: {label_B}</div>", unsafe_allow_html=True)
        extraB = st.multiselect("Colunas extras para ver nos detalhes", options=["ingredientes","beneficios","tipo_pele"], default=[], key=f"extra_cols_cmp_{facet_B}")

        if "produto" in base_B.columns:
            prods = base_B["produto"].dropna().unique().tolist()
            det = df_all[df_all["nome"].isin(prods)].copy()
        else:
            det = df_all[df_all["categoria"] == label_B].copy() if facet_B == "Categoria" else df_all.copy()
        if ms_brands:
            det = det[det[BRAND_COL].isin(ms_brands)]
        render_details_table_products_grouped_by_brand(det, extra_cols=extraB, brand_col=BRAND_COL)

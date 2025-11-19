from __future__ import annotations

from include import *

if "palette_name" not in st.session_state:
    st.session_state["palette_name"] = "Solaris"

apply_palette_css(st.session_state["palette_name"])
SEQ = color_sequence(st.session_state["palette_name"]) or ["#6e56cf", "#22c55e", "#eab308", "#ef4444", "#06b6d4", "#a855f3"]

def accent(i=0): return SEQ[i % len(SEQ)] if SEQ else "#6e56cf"
def accent2(): return SEQ[1] if len(SEQ) > 1 else "#22c55e"
def text_color(): return "#262730"
def subtext_color(): return "#555"
def panel_bg(): return "#ffffff"
def neutral_border(): return "#ececf1"

# Estilo e cabeçalho da página
TITLE_TEXT   = "Tipos de Pele"
TAGLINE_TEXT = (
    "Classificação dos tipos de pele contemplados pelos produtos: acneica, com cicatrizes, com manchas, com olheiras, com poros dilatados, madura, mista, normal, oleosa, seca, sensível ou todos os tipos"
)
TITLE_SIZE   = 56
TAGLINE_SIZE = 24
CHART_H = 640
AXIS_TITLE_SIZE = 22
AXIS_TICK_SIZE  = 20
LEGEND_FONT_SIZE = 32
LEGEND_TITLE_SIZE = 30
TOOLTIP_FONT_SIZE = 22
BARGAP = 0.18
BARGROUPGAP = 0.08

# ===================== CSS (padronizado com a tela de Preço & Quantidade) =====================
st.markdown(f"""
<style>
.page-sub {{ 
    font-size:{TAGLINE_SIZE}px; 
    color:{subtext_color()}; 
    margin:.4rem 0 1.2rem 0; 
}}

/* NOTA */
.mode-description {{
    font-size: 18px;
    color: #555;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 20px;
}}

/* TÍTULO DE SEÇÃO — PRETO */
.section-config {{
    font-size: 22px;
    font-weight: 800;
    color: #000000;
    margin: 16px 0 8px 0;
}}

/* RADIO PILLS */
.stRadio > div[role="radiogroup"] {{
    display: flex; gap: 12px; padding: 0; border: none; background: transparent;
}}
.stRadio > div[role="radiogroup"] > label {{
    background: #fff; border: 1px solid {neutral_border()};
    border-radius: 9999px; padding: 8px 16px; margin: 0 !important;
    font-weight: 700; font-size: 18px !important; color: {text_color()} !important;
    cursor: pointer; transition: all 0.2s ease;
}}
.stRadio > div[role="radiogroup"] > label:hover {{ border-color: {neutral_border()}; background: #fafafa; }}
.stRadio > div[role="radiogroup"] > label > div:first-child {{ display: none !important; }}  /* esconde bolinha */
.stRadio > div[role="radiogroup"] > label[aria-checked="true"] {{
    background: {accent(0)} !important; color: #fff !important; border-color: {accent(0)} !important;
}}

/* ======== PADRÃO DA TABELA (igual à tela Preço & Quantidade) ======== */
.details-table {{
  width: 100%; border-collapse: collapse; margin-top: 1.2rem;
  background: {panel_bg()}; border-radius: 18px; overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,.08);
}}
.details-table thead {{
  background: linear-gradient(135deg, {accent(0)} 0%, {accent(1)} 100%);
  color: white;
}}
.details-table th {{
  padding: 18px 20px; text-align: left; font-weight: 700; font-size: 18px;
  border-bottom: 3px solid rgba(255,255,255,.2);
}}
.details-table td {{
  padding: 16px 20px; font-size: 17px; color: {text_color()};
  border-bottom: 1px solid #f0f0f5;
}}
.details-table tbody tr:hover {{ background: linear-gradient(90deg, {accent(0)}0D 0%, transparent 100%); }}
.details-table tbody tr:last-child td {{ border-bottom: none; }}

/* Título por marca (igual ao Preço & Quantidade) */
.brand-caption {{
  margin-top:18px; margin-bottom:6px; font-weight:900; font-size:22px; color:#fff;
  padding:8px 14px; border-radius:14px;
  background: linear-gradient(90deg, {accent(4)} 0%, {accent(2)} 100%);
}}

/* Subtítulo do bucket (discreto) */
.bucket-caption {{
  display:inline-block; margin:10px 0 6px; padding:8px 12px; border-radius:10px;
  background: {accent(0)}15; color:{accent(0)}; font-weight:800; font-size:16px;
  border-left:4px solid {accent(0)};
}}

/* BOTÕES DE PAGINAÇÃO */
.stButton > button {{
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    padding: 10px 20px !important;
}}
</style>
""", unsafe_allow_html=True)
# ==============================================================================================


#  HELPERS 
def split_semicolon(s: str) -> list[str]:
    if not isinstance(s, str) or not s.strip(): return []
    return [p.strip() for p in s.split(";") if p.strip()]

def to_base_types(raw: str) -> list[str]:
    s = str(raw).lower()
    found = set()
    for canonical, syns in SKIN_TYPE_SYNONYMS_PT.items():
        for term in syns:
            if term and term.lower() in s:
                found.add(canonical.lower()); break
    if "todos" in s and "tipo" in s: found.add("todos os tipos")
    return list(found) or ["(não informado)"]

def explode_skin(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        tipos_raw = split_semicolon(r.get("tipo_pele", "")) or ["(não informado)"]
        for t in tipos_raw:
            rows.append({
                "tipo_pele": t, "nome": r.get("nome"),
                "marca": r.get("marca"), "categoria": r.get("categoria"),
                "beneficios": r.get("beneficios"), "ingredientes": r.get("ingredientes"),
                "preco": r.get("preco"), 
                "quantidade_valor": r.get("quantidade_valor"),
                "quantidade_unidade": r.get("quantidade_unidade")
            })
    return pd.DataFrame(rows)

def style_axes(fig, height: int = CHART_H):
    fig.update_layout(
        font=dict(color=text_color()),
        xaxis=dict(
            title_font=dict(size=AXIS_TITLE_SIZE, color=text_color()),
            tickfont=dict(size=AXIS_TICK_SIZE, color=text_color())
        ),
        yaxis=dict(
            title_font=dict(size=AXIS_TITLE_SIZE, color=text_color()),
            tickfont=dict(size=AXIS_TICK_SIZE, color=text_color())
        ),
        height=height,
        paper_bgcolor=panel_bg(),
        plot_bgcolor=panel_bg(),
        title=None,
        margin=dict(t=60, b=70, l=20, r=260),  # espaço p/ legenda à direita
        hoverlabel=dict(font_size=TOOLTIP_FONT_SIZE, font_color="black", bgcolor="white"),
        legend=dict(font=dict(size=LEGEND_FONT_SIZE), x=1.02, y=1, xanchor="left", yanchor="top"),
        legend_title=dict(text="Marca", font=dict(size=LEGEND_TITLE_SIZE)),
        annotations=[]
    )
    return fig

def product_base_set_series(series: pd.Series) -> set[str]:
    bases: set[str] = set()
    for t in series:
        for b in to_base_types(t):
            bases.add(b)
    return bases

def fmt_price(v):
    try:
        x = float(v); 
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

# ---------- RENDER DA TABELA (igual ao Preço & Quantidade) ----------
# ---------- RENDER DA TABELA (igual ao Preço & Quantidade) ----------
def render_details_table(df: pd.DataFrame):
    """
    Aceita tanto colunas originais (nome, categoria, beneficios, ingredientes)
    quanto as já renomeadas (Produto, Categoria, Benefícios, Ingredientes).
    Garante as colunas obrigatórias e renderiza a tabela .details-table.
    """
    # 1) Normaliza nomes, se vierem no formato original
    col_aliases = {
        "nome": "Produto",
        "categoria": "Categoria",
        "beneficios": "Benefícios",
        "ingredientes": "Ingredientes",
    }
    if any(c in df.columns for c in col_aliases.keys()):
        df = df.rename(columns={k: v for k, v in col_aliases.items() if k in df.columns})

    # 2) Garante que todas as colunas existam
    required = ["Produto", "Categoria", "Quantidade", "Preço", "Benefícios", "Ingredientes"]
    for c in required:
        if c not in df.columns:
            df[c] = "—"

    # 3) Seleciona na ordem certa
    df = df[required].fillna("—")

    # 4) Render HTML padronizado
    headers_map = {
        "Produto": "Produto",
        "Categoria": "Categoria",
        "Quantidade": "Quantidade",
        "Preço": "Preço",
        "Benefícios": "Benefícios",
        "Ingredientes": "Ingredientes",
    }
    thead = "".join([f"<th>{headers_map.get(c, c)}</th>" for c in required])

    rows_html = []
    for _, r in df.iterrows():
        cells = []
        for c in required:
            v = r[c]
            cells.append(f"<td>{v}</td>")
        rows_html.append("<tr>" + "".join(cells) + "</tr>")

    html = f"<table class='details-table'><thead><tr>{thead}</tr></thead><tbody>{''.join(rows_html)}</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)

#  DADOS 
df = load_data()

#  HEADER 
st.markdown(f"<h1 style='margin:0; font-size:{TITLE_SIZE}px; color:{accent(0)}'>{TITLE_TEXT}</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='page-sub'>{TAGLINE_TEXT}</div>", unsafe_allow_html=True)

# GRÁFICO 1 — Todas as marcas × tipos de pele
st.markdown("### Todos os tipos de pele por marca")
st.markdown("""
<div class='mode-description'>
    Este gráfico mostra a distribuição de todos os produtos por tipo de pele para todas as marcas. <br>
    Use a opção <b>Métrica</b> para alternar entre contagem absoluta dos produtos ou participação percentual (%). <br>
    Use os botões <b>Anterior/Próximo</b> para navegar em mais páginas se o gráfico ficar muito extenso.
</div>
""", unsafe_allow_html=True)

# Controles
st.markdown(f"<div class='section-config'>Escolha as configurações do gráfico</div>", unsafe_allow_html=True)
g1_metric = st.radio(
    "Métrica",
    ["Nº de produtos", "Percentual (%) por tipo"],
    horizontal=True,
    key="g1_metric",
    label_visibility="collapsed"
)

ex_all = explode_skin(df)
rows_all = []
for (marca, prod), g in ex_all.groupby(["marca", "nome"]):
    bases = set()
    for t in g["tipo_pele"]:
        bases.update(to_base_types(t))
    for b in bases:
        rows_all.append({"marca": marca, "produto": prod, "tipo_base": b})
presence_all = pd.DataFrame(rows_all)

if presence_all.empty:
    st.info("Sem dados para exibir.")
else:
    dist_all = (presence_all.groupby(["tipo_base","marca"])["produto"]
                .nunique().reset_index(name="produtos"))
    dist_all = dist_all[dist_all["produtos"] > 0]

    all_types = dist_all["tipo_base"].unique().tolist()
    order_types = [t for t in SKIN_TYPE_CANONICAL_ORDER if t in all_types] or sorted(all_types)

    # paginação com botões
    PAGE_SIZE = min(10, len(order_types)) if len(order_types) else 10
    if "g1_page" not in st.session_state: st.session_state["g1_page"] = 0
    start = st.session_state["g1_page"] * PAGE_SIZE
    end = start + PAGE_SIZE
    slice_types = order_types[start:end]

    colp1, colp_mid, colp2 = st.columns([1,6,1])
    with colp1:
        disable_prev = st.session_state["g1_page"] == 0
        if st.button("Página Anterior", key="g1_prev", type="secondary", disabled=disable_prev):
            st.session_state["g1_page"] = max(0, st.session_state["g1_page"] - 1)
    with colp2:
        disable_next = end >= len(order_types)
        if st.button("Próxima Página", key="g1_next", type="secondary", disabled=disable_next):
            st.session_state["g1_page"] = st.session_state["g1_page"] + 1

    dist_all = dist_all[dist_all["tipo_base"].isin(slice_types)]
    order_types = slice_types

    if g1_metric == "Percentual (%) por tipo":
        totals_tipo = dist_all.groupby("tipo_base", as_index=False)["produtos"].sum().rename(columns={"produtos":"total_tipo"})
        dist_all = dist_all.merge(totals_tipo, on="tipo_base", how="left")
        dist_all["valor"] = (dist_all["produtos"] / dist_all["total_tipo"] * 100).round(1)
        y_col, y_label = "valor", "% de produtos no tipo"
        hover = "<b>%{x}</b><br>Marca: <b>%{fullData.name}</b><br>Participação: <b>%{y:.1f}%</b><extra></extra>"
    else:
        dist_all["valor"] = dist_all["produtos"]
        y_col, y_label = "valor", "Nº de produtos"
        hover = "<b>%{x}</b><br>Marca: <b>%{fullData.name}</b><br>Produtos: <b>%{y:.0f}</b><extra></extra>"

    fig_all = px.bar(
        dist_all, x="tipo_base", y=y_col, color="marca", barmode="group",
        color_discrete_sequence=SEQ, category_orders={"tipo_base": order_types},
        labels={"tipo_base":"Tipo de pele", y_col: y_label}
    )
    fig_all.update_traces(hovertemplate=hover)
    fig_all = style_axes(fig_all, height=CHART_H)
    st.plotly_chart(fig_all, width="stretch")

st.markdown("---")

# TABELAS — Encontrar produtos por tipos de pele (com opção de categoria)
st.markdown("### Encontre produtos por tipo de pele")
st.markdown("""
<div class='mode-description'>
    Selecione uma ou mais marcas (ou deixe todas), escolha um ou mais tipos de pele e, opcionalmente, uma categoria.<br>
    Os produtos são organizados em grupos para facilitar a busca:<br>
    <b>CATEGORIA: Todos os tipos</b> - Produtos marcados pelo fabricante como adequados para "todos os tipos de pele".<br>
    <b>APENAS: [tipo]</b> - Produtos que atendem SOMENTE aquele tipo específico (ex: apenas para pele seca).<br>
    <b>EXATAMENTE: [tipo] + [tipo]</b> - Produtos que atendem exatamente a combinação selecionada, sem tipos extras.<br>
    <b>CONTÉM: [tipo]</b> - Produtos que contêm aquele tipo mas também atendem outros tipos de pele.
</div>
""", unsafe_allow_html=True)

# Filtros
brands_all = sorted(df["marca"].dropna().unique().tolist())
sel_brands = st.multiselect("Marcas", options=brands_all, default=brands_all, key="tb_brands")

present_types = sorted({t for t in explode_skin(df)["tipo_pele"].unique() if t})
present_base = sorted({b for t in present_types for b in to_base_types(t)})
type_options = [t for t in SKIN_TYPE_CANONICAL_ORDER if t in present_base]
type_options_with_all = ["Todos os tipos"] + type_options
sel_types_raw = st.multiselect("Tipos de pele", options=type_options_with_all, default=["seca","acneica"], key="tb_types")
sel_types = type_options if "Todos os tipos" in sel_types_raw else sel_types_raw

cats_all = sorted(df[df["marca"].isin(sel_brands)]["categoria"].dropna().unique().tolist())
if CATEGORY_CANONICAL_ORDER:
    cats_all = [c for c in CATEGORY_CANONICAL_ORDER if c in cats_all] + [c for c in cats_all if c not in CATEGORY_CANONICAL_ORDER]
sel_cat = st.selectbox("Categoria (opcional)", options=["(todas)"] + cats_all, index=0, key="tb_cat")

if not sel_brands or not sel_types:
    st.info("Selecione ao menos uma marca e um tipo de pele.")
else:
    base_df = df[df["marca"].isin(sel_brands)].copy()
    if sel_cat != "(todas)":
        base_df = base_df[base_df["categoria"] == sel_cat]

    exp = explode_skin(base_df)
    if exp.empty:
        st.info("Sem dados para a seleção atual.")
    else:
        by_prod = (
            exp.groupby(
                ["marca","nome","categoria","beneficios","ingredientes","preco","quantidade_valor","quantidade_unidade"],
                dropna=False
            )["tipo_pele"]
            .agg(product_base_set_series)
            .reset_index(name="bases")
        )

        def classify_product(bases: set[str], selected: list[str]) -> list[str]:
            """Retorna lista de buckets onde o produto se encaixa"""
            buckets = []
            sel_set = set(selected)

            # 1. Se o produto tem 'todos os tipos' e só isso, entra APENAS
            if bases == {"todos os tipos"}:
                buckets.append("APENAS: todos os tipos")
                return buckets

            # 2. Se contém 'todos os tipos' junto de outros, entra na categoria
            if "todos os tipos" in bases:
                buckets.append("CATEGORIA: Todos os tipos")

            # 3. Verifica tipos individuais
            for tipo in selected:
                if bases == {tipo}:
                    buckets.append(f"APENAS: {tipo}")

            # 4. Combinação exata
            if len(sel_set) > 1 and bases == sel_set:
                tipos_str = " + ".join(sorted(selected))
                buckets.append(f"EXATAMENTE: {tipos_str}")

            # 5. Contém algum tipo (sem ser exclusivo)
            for tipo in selected:
                if tipo in bases and bases != {tipo} and bases != sel_set:
                    buckets.append(f"CONTÉM: {tipo}")

            return buckets

        bucket_rows = []
        for _, row in by_prod.iterrows():
            for bucket in classify_product(row["bases"], sel_types):
                new_row = row.to_dict()
                new_row["bucket"] = bucket
                bucket_rows.append(new_row)
        
        if not bucket_rows:
            st.info("Nenhum produto atende à seleção.")
        else:
            by_prod_exploded = pd.DataFrame(bucket_rows)

            bucket_order = []
            bucket_order.append("CATEGORIA: Todos os tipos")
            for tipo in sel_types:
                bucket_order.append(f"APENAS: {tipo}")
            if len(sel_types) > 1:
                tipos_str = " + ".join(sorted(sel_types))
                bucket_order.append(f"EXATAMENTE: {tipos_str}")
            for tipo in sel_types:
                bucket_order.append(f"CONTÉM: {tipo}")

            # -------- RENDER PADRONIZADO: brand-caption + tabela .details-table --------
            for marca in sel_brands:
                sub = by_prod_exploded[by_prod_exploded["marca"] == marca]
                if sub.empty:
                    continue
                
                st.markdown(f"<div class='brand-caption'>{marca}</div>", unsafe_allow_html=True)
                
                for bucket in bucket_order:
                    tb = sub[sub["bucket"] == bucket].copy()
                    if tb.empty:
                        continue

                    # subtítulo discreto do bucket
                    st.markdown(f"<span class='bucket-caption'>{bucket}</span>", unsafe_allow_html=True)

                    tb["Preço"] = tb["preco"].apply(fmt_price)
                    tb["Quantidade"] = tb.apply(lambda r: fmt_qtd(r["quantidade_valor"], r["quantidade_unidade"]), axis=1)

                    display_tb = (
                        tb[["nome","categoria","Quantidade","Preço","beneficios","ingredientes"]]
                        .rename(columns={"nome":"Produto","categoria":"Categoria","beneficios":"Benefícios","ingredientes":"Ingredientes"})
                        .fillna("—")
                        .drop_duplicates()
                    )

                    # mesma tabela HTML da outra tela
                    render_details_table(display_tb)

            st.markdown("---")
            st.markdown("### Visualizações resumidas da sua seleção")
            st.markdown("""
                <div class='mode-description'>
                Quantos produtos de cada marca caíram em cada grupo mostrado nas tabelas (empilhado ou agrupado).<br>
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

            bar_mode = st.radio("Modo de Exibição do Gráfico", ["Empilhado", "Agrupado"], horizontal=True, key="g_sum_mode")
            barmode = "stack" if bar_mode == "Empilhado" else "group"

            fig_sum = px.bar(
                agg_bucket, x="marca", y="produtos", color="bucket", barmode=barmode,
                color_discrete_sequence=SEQ,
                labels={"marca":"Marca", "produtos":"Nº de produtos", "bucket":"Marca"},
            )
            fig_sum.update_traces(
                hovertemplate="<b>%{x}</b><br>Marca: <b>%{fullData.name}</b><br>Produtos: <b>%{y}</b><extra></extra>"
            )

            style_axes(fig_sum, height=720)
            st.plotly_chart(fig_sum, width="stretch")

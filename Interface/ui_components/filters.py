from __future__ import annotations
from include import *  

# Helpers
def _pretty_from_source(fname: str) -> str:
    """Converte nome do arquivo CSV em nome de marca legível."""
    stem = Path(fname).stem
    for suf in ["_products", "_skincare", "_cosmetics", "_dados"]:
        stem = stem.replace(suf, "")
    return stem.replace("_", " ").title()

# Filtros por Categoria
def render_filters_por_categoria(df: pd.DataFrame) -> Tuple[List[str], List[str], str]:
    sel_files: List[str] = []

    st.markdown("""
    <style>
    .filter-label {
        font-size: 22px;
        font-weight: 600;
        color: #363636;
        display: block;
        margin: 12px 0 6px;
    }
    </style>
    """, unsafe_allow_html=True)

    #  Filtro de Marcas 
    st.markdown("<span class='filter-label'>Marcas</span>", unsafe_allow_html=True)

    if "_source_file" in df.columns:
        files = sorted(df["_source_file"].dropna().unique().tolist())
        label_map = {_pretty_from_source(f): f for f in files}
        labels = list(label_map.keys())

        sel_labels = st.multiselect(
            label="Marcas (multiseleção)",
            options=labels,
            default=labels,
            key="flt_marcas_cat",
            label_visibility="collapsed",
        )
        sel_files = [label_map[l] for l in sel_labels]
    else:
        marcas = sorted(df["marca"].dropna().unique().tolist()) if "marca" in df.columns else []
        sel_m = st.multiselect(
            label="Marcas (multiseleção)",
            options=marcas,
            default=marcas,
            key="flt_marcas_cat_fb",
            label_visibility="collapsed",
        )
        st.session_state["_fallback_marcas"] = sel_m

    #  Filtro de Categoria 
    st.markdown("<span class='filter-label'>Escolha Uma Categoria</span>", unsafe_allow_html=True)
    cat_opts = CATEGORY_CANONICAL_ORDER[:] if CATEGORY_CANONICAL_ORDER else []

    if not cat_opts:
        st.warning("Nenhuma categoria encontrada em category.py")
        return sel_files, [], "Quantidade (decrescente)"

    sel_cat = st.selectbox(
        label="Categoria (seleção única)",
        options=cat_opts,
        index=0,
        key="flt_categoria_cat",
        label_visibility="collapsed",
    )

    #  Ordenação 
    st.markdown("<span class='filter-label'>Ordenar Por</span>", unsafe_allow_html=True)
    order_option = st.radio(
        label="Ordenar por",
        options=["Quantidade (decrescente)", "Quantidade (crescente)", "Alfabética"],
        key="flt_ordem_cat",
        label_visibility="collapsed",
        horizontal=False,
    )

    return sel_files, [sel_cat], order_option

# Filtros por Marca
def render_filters_por_marca(df: pd.DataFrame) -> Tuple[str, str]:
    st.markdown("""
    <style>
    .filter-label {
        font-size: 22px;
        font-weight: 600;
        color: #363636;
        display: block;
        margin: 12px 0 6px;
    }
    </style>
    """, unsafe_allow_html=True)

    #  Filtro de Marca 
    st.markdown("<span class='filter-label'>Escolha Uma Marca</span>", unsafe_allow_html=True)

    if "_source_file" in df.columns:
        files = sorted(df["_source_file"].dropna().unique().tolist())
        label_map = {_pretty_from_source(f): f for f in files}
        labels = list(label_map.keys())

        if not labels:
            st.warning("Nenhuma marca encontrada nos arquivos.")
            return "", "Quantidade (decrescente)"

        sel_label = st.selectbox(
            label="Marca (seleção única)",
            options=labels,
            index=0,
            key="flt_marca_marca",
            label_visibility="collapsed",
        )
        sel_marca_file = label_map[sel_label] if sel_label else ""
    else:
        marcas = sorted(df["marca"].dropna().unique().tolist()) if "marca" in df.columns else []
        if not marcas:
            st.warning("Nenhuma marca encontrada.")
            return "", "Quantidade (decrescente)"

        sel_marca_file = st.selectbox(
            label="Marca (seleção única)",
            options=marcas,
            index=0,
            key="flt_marca_marca_fb",
            label_visibility="collapsed",
        )

    st.markdown(
        "<p style='font-size:16px; color:#666; font-style:italic; margin-top:10px;'>O gráfico exibirá a distribuição de produtos por categoria apenas para a marca selecionada.</p>",
        unsafe_allow_html=True
    )

    #  Ordenação 
    st.markdown("<span class='filter-label'>Ordenar Por</span>", unsafe_allow_html=True)
    order_option = st.radio(
        label="Ordenar por",
        options=["Quantidade (decrescente)", "Quantidade (crescente)", "Alfabética"],
        key="flt_ordem_marca",
        label_visibility="collapsed",
        horizontal=False,
    )

    return sel_marca_file, order_option

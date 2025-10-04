# ui_components/filters.py
from __future__ import annotations
from pathlib import Path
import sys
from typing import List, Tuple
import streamlit as st
import pandas as pd

# Models (ordem canônica de categorias)
sys.path.append("/home/usuario/Área de trabalho/Dados/models")
try:
    from category import CATEGORY_CANONICAL_ORDER  # type: ignore
except Exception:
    CATEGORY_CANONICAL_ORDER = []

def _pretty_from_source(fname: str) -> str:
    stem = Path(fname).stem
    for suf in ["_products", "_skincare", "_cosmetics", "_dados"]:
        stem = stem.replace(suf, "")
    return stem.replace("_", " ").title()

def render_global_filters(df: pd.DataFrame) -> Tuple[List[str], List[str], str]:
    """
    Retorna:
      - sel_files: lista de arquivos selecionados (quando _source_file existir) ou []
      - [sel_cat]: lista com 1 categoria selecionada (string)
      - order_option: string com a opção de ordenação
    """
    sel_files: List[str] = []

    # ===== MARCA =====
    st.markdown("<span class='filter-label'>Marca</span>", unsafe_allow_html=True)
    if "_source_file" in df.columns:
        files = sorted(df["_source_file"].dropna().unique().tolist())
        label_map = {_pretty_from_source(f): f for f in files}
        labels = list(label_map.keys())

        # <<< label NÃO vazio + label_visibility="collapsed" >>>
        sel_labels = st.multiselect(
            label="Marcas (multiseleção)",
            options=labels,
            default=labels,
            key="flt_marcas_labels",
            label_visibility="collapsed",
        )
        sel_files = [label_map[l] for l in sel_labels]
    else:
        marcas = sorted(df["marca"].dropna().unique().tolist()) if "marca" in df.columns else []
        sel_m = st.multiselect(
            label="Marcas (multiseleção)",
            options=marcas,
            default=marcas,
            key="flt_marcas_fallback",
            label_visibility="collapsed",
        )
        st.session_state["_fallback_marcas"] = sel_m  # usado em outras telas se necessário

    # ===== CATEGORIA =====
    st.markdown("<span class='filter-label'>Categoria</span>", unsafe_allow_html=True)
    cat_opts = CATEGORY_CANONICAL_ORDER[:] if CATEGORY_CANONICAL_ORDER else []
    sel_cat = st.selectbox(
        label="Categoria",
        options=cat_opts,
        index=0 if cat_opts else None,
        key="flt_categoria",
        label_visibility="collapsed",
    )

    # ===== ORDENAR =====
    # CSS opcional para o radio (mantive seu estilo)
    st.markdown(
        """
        <style>
        .filter-label {
            font-size: 32px;
            font-weight: 700;
            color: #262730;
            margin-bottom: 6px;
        }
        div[role="radiogroup"] label {
            font-size: 28px !important;
            color: #363636 !important;
            font-weight: 800 !important;
            padding: 6px 0 !important;
        }
        div[role="radiogroup"] input[type="radio"] {
            width: 22px !important;
            height: 22px !important;
            margin-right: 8px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<span class='filter-label'>Ordenar Por</span>", unsafe_allow_html=True)
    order_option = st.radio(
        label="Ordenar por",
        options=["Quantidade (decrescente)", "Quantidade (crescente)", "Alfabética"],
        key="flt_ordem",
        label_visibility="collapsed",
        horizontal=False,
    )

    return sel_files, [sel_cat], order_option

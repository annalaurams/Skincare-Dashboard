# ui_components/filters.py
from __future__ import annotations
from pathlib import Path
import sys
from typing import List, Tuple
import streamlit as st
import pandas as pd

# importa a lista canônica (todas as categorias possíveis)
sys.path.append("/home/usuario/Área de trabalho/Dados/models")
from category import CATEGORY_CANONICAL_ORDER  # noqa: E402


# =========================
# Utilidades internas
# =========================
def _pretty_from_source(fname: str) -> str:
    """
    Converte um nome de arquivo CSV para um rótulo “humano”.
    Ex.: 'sallve_products.csv' -> 'Sallve'
    """
    stem = Path(fname).stem
    for suf in ["_products", "_skincare", "_cosmetics", "_dados"]:
        stem = stem.replace(suf, "")
    return stem.replace("_", " ").title()


# =========================
# Filtro “global” (para páginas que usam arquivos como marcas)
# =========================
def render_global_filters(df: pd.DataFrame) -> Tuple[List[str], List[str]]:
    """
    Filtro ÚNICO:
      - Marca => por ARQUIVOS (_source_file), quando existir essa coluna.
                 (se não existir, cai em fallback por coluna 'marca')
      - Categoria => seleção pela lista canônica CATEGORY_CANONICAL_ORDER

    Retorna:
      (lista_de_arquivos_escolhidos, lista_de_categorias_escolhidas)
    """
    st.markdown("#### Aplicar filtros")

    # --- Marca = arquivo (se disponível) ---
    sel_files: List[str] = []
    if "_source_file" in df.columns:
        files = sorted(df["_source_file"].dropna().unique().tolist())
        label_map = { _pretty_from_source(f): f for f in files }
        labels = list(label_map.keys())

        sel_labels = st.multiselect("Marca", options=labels, default=labels)
        sel_files = [label_map[l] for l in sel_labels]
    else:
        # fallback se _source_file não existir
        marcas = sorted(df["marca"].dropna().unique().tolist())
        sel_m = st.multiselect("Marca", options=marcas, default=marcas)
        # guardamos para uso eventual
        st.session_state["_fallback_marcas"] = sel_m

    # --- Categorias (sempre a lista canônica completa) ---
    cat_opts = CATEGORY_CANONICAL_ORDER[:]  # todas as categorias do models/category.py
    sel_cats = st.multiselect("Categoria do Produto", options=cat_opts, default=[])

    return sel_files, sel_cats


# =========================
# Helpers reutilizáveis (para outras páginas)
# =========================
def pick_marcas(df: pd.DataFrame, key_prefix: str = "", default_all: bool = False) -> List[str]:
    """
    Multiselect de marcas com base na coluna 'marca'.
    - default_all=True pré-seleciona todas as marcas.
    """
    marcas = sorted(df["marca"].dropna().unique().tolist())
    default = marcas if default_all else []
    return st.multiselect(
        "Marca",
        options=marcas,
        default=default,
        key=f"{key_prefix}_marcas"
    )


def pick_categorias(
    df: pd.DataFrame,
    key_prefix: str = "",
    use_canonical: bool = True,
    default_all: bool = False
) -> List[str]:
    """
    Multiselect de categorias.
    - use_canonical=True: usa a lista canônica do models/category.py (mostra TODAS).
      use_canonical=False: usa apenas as categorias presentes no DF filtrado.
    - default_all=True pré-seleciona todas as opções.
    """
    if use_canonical:
        categorias = CATEGORY_CANONICAL_ORDER[:]
        # opcionalmente, pode destacar as que existem de fato no df (não filtra, só ordena)
        have = sorted(set(df["categoria"].dropna().unique()))
        # coloca as que existem primeiro
        categorias = sorted(categorias, key=lambda c: (c not in have, c))
    else:
        categorias = sorted(df["categoria"].dropna().unique().tolist())

    default = categorias if default_all else []
    return st.multiselect(
        "Categoria do Produto",
        options=categorias,
        default=default,
        key=f"{key_prefix}_cats"
    )


def pick_one_marca(df: pd.DataFrame, key_prefix: str = "", placeholder: str = "Escolha uma marca") -> str | None:
    """
    Selectbox para escolher UMA marca (retorna string ou None).
    """
    marcas = sorted(df["marca"].dropna().unique().tolist())
    if not marcas:
        st.info("Nenhuma marca disponível.")
        return None
    idx = 0 if marcas else None
    sel = st.selectbox("Marca (uma)", options=marcas, index=idx, key=f"{key_prefix}_one_marca", placeholder=placeholder)
    return sel


def pick_one_categoria(
    df: pd.DataFrame,
    key_prefix: str = "",
    use_canonical: bool = True,
    placeholder: str = "Escolha uma categoria"
) -> str | None:
    """
    Selectbox para escolher UMA categoria (retorna string ou None).
    - use_canonical=True: mostra a lista canônica inteira.
      False: só categorias presentes no DF.
    """
    if use_canonical:
        categorias = CATEGORY_CANONICAL_ORDER[:]
    else:
        categorias = sorted(df["categoria"].dropna().unique().tolist())

    if not categorias:
        st.info("Nenhuma categoria disponível.")
        return None

    # se possível, coloca a mais frequente como default
    if not use_canonical and "categoria" in df.columns and not df.empty:
        freq = df["categoria"].value_counts()
        default_val = freq.index[0]
        try:
            default_idx = categorias.index(default_val)
        except ValueError:
            default_idx = 0
    else:
        default_idx = 0

    sel = st.selectbox("Categoria (uma)", options=categorias, index=default_idx,
                       key=f"{key_prefix}_one_cat", placeholder=placeholder)
    return sel


# =========================
# Opcional: seleção por arquivo (quando quiser filtrar por CSV específico)
# =========================
def pick_source_files(df: pd.DataFrame, key_prefix: str = "", default_all: bool = True) -> List[str]:
    """
    Multiselect de ARQUIVOS (quando o DF foi carregado de vários CSVs e possui a coluna '_source_file').
    Retorna a lista de nomes de arquivo selecionados.
    """
    if "_source_file" not in df.columns:
        return []

    files = sorted(df["_source_file"].dropna().unique().tolist())
    labels = { _pretty_from_source(f): f for f in files }
    opts = list(labels.keys())
    default = opts if default_all else []

    sel_labels = st.multiselect("Arquivos (marcas)", options=opts, default=default, key=f"{key_prefix}_files")
    return [labels[l] for l in sel_labels]

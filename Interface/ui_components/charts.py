# ui_components/charts.py
from __future__ import annotations
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from core.theme import color_sequence

# importa lista canônica
sys.path.append("/home/usuario/Área de trabalho/Dados/models")
from category import CATEGORY_CANONICAL_ORDER  # noqa: E402

def apply_filters(
    df: pd.DataFrame,
    marcas: list[str] | None,
    cats: list[str] | None,
    source_files: list[str] | None = None
) -> pd.DataFrame:
    out = df.copy()
    # 1) Filtra pelos arquivos (marca == CSV)
    if source_files is not None and "_source_file" in out.columns:
        if source_files:
            out = out[out["_source_file"].isin(source_files)]
        else:
            return out.iloc[0:0]
    # 2) (opcional) fallback por coluna 'marca' se você usar isso em outro lugar
    if marcas:
        out = out[out["marca"].isin(marcas)]
    # 3) Categoria selecionada
    if cats:
        out = out[out["categoria"].isin(cats)]
    return out
def chart_produtos_por_categoria(
    df: pd.DataFrame,
    palette_name: str,
    key_prefix: str = "cat",
    # ▼ CONTROLES NOVOS
    show_bottom_legend: bool = False,   # False = sem legenda embaixo
    legend_size: int = 20,              # tamanho da fonte da legenda
    itemwidth: int = 180,               # “largura” de item p/ quebrar em colunas
    legend_y: float = -0.45,            # distância vertical da legenda (barras)
    margin_b: int = 180,                # margem inferior extra p/ caber a legenda
    bar_text_size: int = 16             # fonte dos números nas barras
):
    import math

    st.markdown(
        "<span style='font-size:28px; font-weight:500;'>Distribuição de Produtos por Categoria</span>",
        unsafe_allow_html=True
    )
    if df.empty:
        st.warning("Nenhum dado para exibir.")
        return

    # Contagem por LINHAS (cada produto = 1 linha)
    dist = (
        df.groupby("categoria")["nome"].size()
          .reset_index(name="quantidade")
    )

    # Ordena por ordem canônica
    dist["categoria"] = pd.Categorical(
        dist["categoria"], categories=CATEGORY_CANONICAL_ORDER, ordered=True
    )
    dist = dist.sort_values(["categoria"]).reset_index(drop=True)

    if dist.empty:
        st.info("Não há categorias com produtos para os filtros atuais.")
        return

    seq = color_sequence(palette_name)
    tabs = st.tabs(["Barras", "Rosca"])

    # -------------------- BARRAS --------------------
    with tabs[0]:
        orient = st.radio(
            "Orientação",
            ["Vertical", "Horizontal"],
            horizontal=True,
            key=f"orient_{key_prefix}"
        )

        if orient == "Vertical":
            fig = px.bar(
                dist, x="categoria", y="quantidade",
                color="categoria", color_discrete_sequence=seq,
                text="quantidade",
                labels={"categoria": "Categoria", "quantidade": "Número de produtos"}
            )
            fig.update_traces(textposition="outside",
                              textfont=dict(size=bar_text_size, color="#363636"))
        else:
            fig = px.bar(
                dist, x="quantidade", y="categoria", orientation="h",
                color="categoria", color_discrete_sequence=seq,
                text="quantidade",
                labels={"categoria": "Categoria", "quantidade": "Número de produtos"}
            )
            fig.update_traces(textposition="outside",
                              textfont=dict(size=bar_text_size, color="#363636"))

        # ====== LEGENDA (REMOVIDA OU EMBAIXO) ======
        n_items = dist["categoria"].nunique()
        cols = 1 if itemwidth <= 0 else max(1, math.floor(1000 / itemwidth))  # estimativa de colunas
        rows = math.ceil(n_items / max(1, cols))

        # layout base
        layout_kwargs = dict(
            height=750,  # mais comprido pra não cortar textos
            legend_title_text="",         # remove o “Categoria”
            xaxis_tickangle=-20 if orient == "Vertical" else 0,
            xaxis=dict(title_font=dict(size=18, color="#363636"),
                       tickfont=dict(size=14, color="#363636")),
            yaxis=dict(title_font=dict(size=18, color="#363636"),
                       tickfont=dict(size=14, color="#363636")),
            margin=dict(t=80, b=100 if not show_bottom_legend else margin_b, r=20, l=20),
        )

        if show_bottom_legend:
            layout_kwargs.update(dict(
                showlegend=True,
                legend=dict(
                    orientation="h",
                    y=legend_y - (rows-1)*0.02,  # empurra conforme nº de linhas
                    x=0.5, xanchor="center",
                    itemwidth=itemwidth if itemwidth > 0 else None,
                    traceorder="normal",
                    font=dict(size=legend_size, color="#363636")
                ),
            ))
        else:
            layout_kwargs.update(dict(showlegend=False))

        fig.update_layout(**layout_kwargs)
        # Evita que os textos “cortem” na borda
        fig.update_yaxes(automargin=True)
        fig.update_xaxes(automargin=True)
        st.plotly_chart(fig, use_container_width=True)

    # -------------------- ROSCA --------------------
    with tabs[1]:
        figp = px.pie(
            dist, names="categoria", values="quantidade",
            hole=0.55, color="categoria", color_discrete_sequence=seq
        )
        figp.update_traces(textposition="inside", textinfo="percent+label",
                           textfont=dict(size=18, color="#363636"))

        # legenda ao lado, levemente mais para dentro; sem título
        figp.update_layout(
            height=650,
            margin=dict(t=60, b=40, l=40, r=140),
            legend_title_text="",
            legend=dict(
                x=0.86, xanchor="left",
                y=0.98, yanchor="top",
                font=dict(size=25, color="#363636")
            )
        )
        st.plotly_chart(figp, use_container_width=True)

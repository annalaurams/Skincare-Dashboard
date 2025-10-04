from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from core.theme import color_sequence

sys.path.append("/home/usuario/Área de trabalho/Dados/models")
try:
    from category import CATEGORY_CANONICAL_ORDER
except Exception:
    CATEGORY_CANONICAL_ORDER = None

def apply_filters(
    df: pd.DataFrame,
    marcas: list[str] | None,
    cats: list[str] | None,
    source_files: list[str] | None = None
) -> pd.DataFrame:
    out = df.copy()
    if source_files is not None and "_source_file" in out.columns:
        if source_files:
            out = out[out["_source_file"].isin(source_files)]
        else:
            return out.iloc[0:0]
    if marcas:
        out = out[out["marca"].isin(marcas)]
    if cats:
        out = out[out["categoria"].isin(cats)]
    return out

def _pretty_from_source(fname: str) -> str:
    stem = Path(fname).stem
    # for suf in ["_products", "_skincare", "_cosmetics", "_dados"]:
    for suf in ["_products"]:
        stem = stem.replace(suf, "")
    return stem.replace("_", " ").title()


def chart_produtos_por_categoria(
    df: pd.DataFrame,
    palette_name: str,
    key_prefix: str = "cat",
    show_bottom_legend: bool = False,
    legend_size: int = 30,
    itemwidth: int = 180,
    legend_y: float = -0.45,
    margin_b: int = 180,
    bar_text_size: int = 18,
    selected_files: list[str] | None = None,
    hover_box: str = "right",
    order_option: str | None = None,
    show_internal_title: bool = False
):
    import math

    if df.empty:
        st.warning("Nenhum dado para exibir.")
        return

    # tooltip
    cats = sorted([c for c in df["categoria"].dropna().unique().tolist()])
    cat_title = cats[0] if len(cats) == 1 else "Várias categorias"

    uses_files = "_source_file" in df.columns
    if uses_files:
        base = df[df["_source_file"].isin(selected_files)].copy() if selected_files else df.copy()
        dist = base.groupby("_source_file")["nome"].size().reset_index(name="quantidade")
        dist["marca"] = dist["_source_file"].apply(_pretty_from_source)
        key_col = "_source_file"
        label_col = "marca"
    else:
        base = df.copy()
        if "marca" not in base.columns:
            st.warning("Não há coluna de marca nem _source_file para segmentar.")
            return
        dist = base.groupby("marca")["nome"].size().reset_index(name="quantidade")
        key_col = "marca"
        label_col = "marca"

    if order_option == "Quantidade (crescente)":
        dist = dist.sort_values(["quantidade", label_col], ascending=[True, True]).reset_index(drop=True)
    elif order_option == "Alfabética":
        dist = dist.sort_values(label_col, ascending=True).reset_index(drop=True)
    elif order_option == "Ordem Canônica" and CATEGORY_CANONICAL_ORDER:

        _CAT_ORDER_MAP = {c: i for i, c in enumerate(CATEGORY_CANONICAL_ORDER)}
        dist["cat_order"] = dist[label_col].map(_CAT_ORDER_MAP).fillna(9999)
        dist = dist.sort_values(["cat_order", label_col]).reset_index(drop=True)
        dist = dist.drop(columns=["cat_order"])
    else:
        dist = dist.sort_values(["quantidade", label_col], ascending=[False, True]).reset_index(drop=True)

    seq = color_sequence(palette_name)
    tabs = st.tabs(["Barras", "Rosca"])

    # BARRAS 
    with tabs[0]:
        hovermode_layout = {"hovermode": "closest",
                            "hoverlabel": dict(font_size=22, font_color="gray", bgcolor="white", align="left")}

        fig = px.bar(
            dist,
            x=label_col, y="quantidade",
            text="quantidade",
            labels={label_col: "Marca", "quantidade": "Número de produtos"},
            hover_data={}
        )
        # cores por barra 
        colors = (seq * ((len(dist) // max(1, len(seq))) + 1))[:len(dist)]
        fig.update_traces(
            marker_color=colors,
            textposition="outside",
            textfont=dict(size=bar_text_size, color="#363636"),
            hovertemplate="<b>%{x}</b><br>Categoria: <b>" + cat_title + "</b><br>Quantidade: %{y}<extra></extra>"
        )

        n_items = dist[label_col].nunique()
        cols = 1 if itemwidth <= 0 else max(1, math.floor(1000 / itemwidth))
        rows = math.ceil(n_items / max(1, cols))

        layout_kwargs = dict(
            height=750,
            legend_title_text="",
            xaxis_tickangle=-15,
            xaxis=dict(title_font=dict(size=28, color="#363636"),
                       tickfont=dict(size=22, color="#363636")),
            yaxis=dict(title_font=dict(size=28, color="#363636"),
                       tickfont=dict(size=22, color="#363636")),
            margin=dict(t=40, b=100 if not show_bottom_legend else margin_b, r=20, l=20),
            title=dict(text=f"Categoria: {cat_title}", font=dict(size=24, color="#363636"))
        )
        # if show_bottom_legend:
        #     layout_kwargs.update(dict(
        #         showlegend=True,
        #         legend=dict(
        #             orientation="h",
        #             y=legend_y - (rows-1)*0.02,
        #             x=0.5, xanchor="center",
        #             itemwidth=itemwidth if itemwidth > 0 else None,
        #             traceorder="normal",
        #             font=dict(size=legend_size, color="#363636")
        #         ),
        #     ))
        # else:
        layout_kwargs.update(dict(showlegend=False))

        fig.update_layout(**layout_kwargs, **hovermode_layout)
        fig.update_yaxes(automargin=True)
        fig.update_xaxes(automargin=True)
        st.plotly_chart(fig, use_container_width=True)

    # ROSCA 
    with tabs[1]:
        figp = px.pie(
            dist,
            names=label_col, values="quantidade",
            hole=0.55, color=label_col, color_discrete_sequence=seq
        )
        figp.update_traces(
            textposition="inside", textinfo="percent+label",
            textfont=dict(size=28, color="#363636"),
            hovertemplate="<b>%{label}</b><br>Categoria: <b>" + cat_title + "</b><br>Quantidade: %{value} (%{percent:.1%})<extra></extra>"
        )
        figp.update_layout(
            height=750,
            margin=dict(t=40, b=40, l=40, r=140),
            legend_title_text="",
            legend=dict(
                x=0.86, xanchor="left",
                y=0.98, yanchor="top",
                font=dict(size=30, color="#363636")
            ),
            title=dict(text=f"Categoria: {cat_title}", font=dict(size=24, color="#363636")),
            hoverlabel=dict(font_size=22, font_color="gray", bgcolor="white", align="left")
        )
        st.plotly_chart(figp, use_container_width=True)

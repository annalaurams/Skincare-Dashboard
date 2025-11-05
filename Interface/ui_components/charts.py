from __future__ import annotations
from include import *          
from pathlib import Path      

def _pick(seq, i, fallback=0):
    return seq[i] if i < len(seq) else seq[fallback]

def _gradient(a: str, b: str) -> str:
    return f"linear-gradient(135deg, {a} 0%, {b} 100%)"

def _render_summary_cards(total_left: int, label_left: str, total_right: int, label_right: str, seq):
    g1_from = _pick(seq, 0)
    g1_to   = _pick(seq, 1, fallback=0)
    g2_from = _pick(seq, 2, fallback=0)
    g2_to   = _pick(seq, 3, fallback=1)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div style="background: {_gradient(g1_from, g1_to)};
                 border-radius: 12px; padding: 20px; text-align: center; color: white;">
                <div style="font-size: 42px; font-weight: bold;">{total_left}</div>
                <div style="font-size: 28px; opacity: 0.9;">{label_left}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div style="background: {_gradient(g2_from, g2_to)};
                 border-radius: 12px; padding: 20px; text-align: center; color: white;">
                <div style="font-size: 42px; font-weight: bold;">{total_right}</div>
                <div style="font-size: 28px; opacity: 0.9;">{label_right}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

#  Funções de Filtro
def apply_filters(df: pd.DataFrame, marcas=None, cats=None, source_files=None) -> pd.DataFrame:
    out = df.copy()

    if source_files is not None and "_source_file" in out.columns:
        out = out[out["_source_file"].isin(source_files)] if source_files else out.iloc[0:0]

    if marcas:
        out = out[out["marca"].isin(marcas)]
    if cats:
        out = out[out["categoria"].isin(cats)]

    return out

def _pretty_from_source(fname: str) -> str:
    stem = Path(fname).stem
    for suf in ["_products"]:
        stem = stem.replace(suf, "")
    return stem.replace("_", " ").title()

# GRÁFICO 1: PRODUTOS POR CATEGORIA (múltiplas marcas, 1 categoria)
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

    # Identifica a categoria selecionada
    cats = sorted([c for c in df["categoria"].dropna().unique().tolist()])
    cat_title = cats[0] if len(cats) == 1 else "Várias categorias"

    # Agrupa por marca 
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

    #  ordenação
    if order_option == "Quantidade (crescente)":
        dist = dist.sort_values(["quantidade", label_col], ascending=[True, True]).reset_index(drop=True)
    elif order_option == "Alfabética":
        dist = dist.sort_values(label_col, ascending=True).reset_index(drop=True)
    else: 
        dist = dist.sort_values(["quantidade", label_col], ascending=[False, True]).reset_index(drop=True)

    seq = color_sequence(palette_name)
    tabs = st.tabs(["Barras (Quantidade de Produtos)", "Rosca (Porcentagem de Produtos)"])

    # TAB: GRÁFICO DE BARRAS
    with tabs[0]:
        hovermode_layout = {
            "hovermode": "closest",
            "hoverlabel": dict(font_size=22, font_color="gray", bgcolor="white", align="left")
        }

        fig = px.bar(
            dist,
            x=label_col, y="quantidade",
            text="quantidade",
            labels={label_col: "Marca", "quantidade": "Número de produtos"},
            hover_data={}
        )

        # Aplica cores diferentes para cada barra
        colors = (seq * ((len(dist) // max(1, len(seq))) + 1))[:len(dist)]
        fig.update_traces(
            marker_color=colors,
            textposition="outside",
            textfont=dict(size=bar_text_size, color="#363636"),
            hovertemplate="<b>%{x}</b><br>Categoria: <b>" + cat_title + "</b><br>Quantidade: %{y}<extra></extra>"
        )

        layout_kwargs = dict(
            height=750,
            legend_title_text="",
            xaxis_tickangle=-15,
            xaxis=dict(
                title_font=dict(size=28, color="#363636"),
                tickfont=dict(size=22, color="#363636")
            ),
            yaxis=dict(
                title_font=dict(size=28, color="#363636"),
                tickfont=dict(size=22, color="#363636")
            ),
            margin=dict(t=40, b=100, r=20, l=20),
            title=dict(text=f"Categoria: {cat_title}", font=dict(size=24, color="#363636")),
            showlegend=False
        )

        fig.update_layout(**layout_kwargs, **hovermode_layout)
        fig.update_yaxes(automargin=True)
        fig.update_xaxes(automargin=True)
        st.plotly_chart(fig, use_container_width=True)

        seq_cards = color_sequence(palette_name)
        total_produtos = int(dist["quantidade"].sum())
        total_categorias = 1 
        _render_summary_cards(
            total_left=total_produtos, label_left="Total de Produtos",
            total_right=total_categorias, label_right="Total de Categoria Selecionadas",
            seq=seq_cards
        )

    # TAB: GRÁFICO DE ROSCA
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

        seq_cards = color_sequence(palette_name)
        total_produtos = int(dist["quantidade"].sum())
        total_categorias = 1
        _render_summary_cards(
            total_left=total_produtos, label_left="Total de Produtos",
            total_right=total_categorias, label_right="Categoria Selecionada",
            seq=seq_cards
        )

# GRÁFICO 2: CATEGORIAS POR MARCA (1 marca, TODAS as categorias)
def chart_categorias_por_marca(
    df: pd.DataFrame,
    palette_name: str,
    key_prefix: str = "marca",
    legend_size: int = 30,
    bar_text_size: int = 18,
    order_option: str | None = None,
    show_internal_title: bool = False
):
    import math

    if df.empty:
        st.warning("Nenhum dado para exibir.")
        return

    # Identifica a marca 
    uses_files = "_source_file" in df.columns
    if uses_files:
        marca_files = df["_source_file"].dropna().unique().tolist()
        marca_name = _pretty_from_source(marca_files[0]) if len(marca_files) == 1 else "Várias marcas"
    else:
        marcas = df["marca"].dropna().unique().tolist() if "marca" in df.columns else []
        marca_name = marcas[0] if len(marcas) == 1 else "Várias marcas"

    # Agrupa por categoria 
    dist = df.groupby("categoria")["nome"].size().reset_index(name="quantidade")

    # ordenação
    if order_option == "Quantidade (crescente)":
        dist = dist.sort_values(["quantidade", "categoria"], ascending=[True, True]).reset_index(drop=True)
    elif order_option == "Alfabética":
        dist = dist.sort_values("categoria", ascending=True).reset_index(drop=True)
    elif order_option == "Ordem Canônica" and CATEGORY_CANONICAL_ORDER:

        _CAT_ORDER_MAP = {c: i for i, c in enumerate(CATEGORY_CANONICAL_ORDER)}
        dist["cat_order"] = dist["categoria"].map(_CAT_ORDER_MAP).fillna(9999)
        dist = dist.sort_values(["cat_order", "categoria"]).reset_index(drop=True)
        dist = dist.drop(columns=["cat_order"])
    else: 
        dist = dist.sort_values(["quantidade", "categoria"], ascending=[False, True]).reset_index(drop=True)

    seq = color_sequence(palette_name)
    tabs = st.tabs(["Barras", "Rosca"])

    # TAB: GRÁFICO DE BARRAS
    with tabs[0]:
        hovermode_layout = {
            "hovermode": "closest",
            "hoverlabel": dict(font_size=22, font_color="gray", bgcolor="white", align="left")
        }

        fig = px.bar(
            dist,
            x="categoria", y="quantidade",
            text="quantidade",
            labels={"categoria": "Categoria", "quantidade": "Número de produtos"},
            hover_data={}
        )

        # Aplica cores diferentes para cada barra
        colors = (seq * ((len(dist) // max(1, len(seq))) + 1))[:len(dist)]
        fig.update_traces(
            marker_color=colors,
            textposition="outside",
            textfont=dict(size=bar_text_size, color="#363636"),
            hovertemplate="<b>%{x}</b><br>Marca: <b>" + marca_name + "</b><br>Quantidade: %{y}<extra></extra>"
        )

        layout_kwargs = dict(
            height=750,
            legend_title_text="",
            xaxis_tickangle=-15,
            xaxis=dict(
                title_font=dict(size=28, color="#363636"),
                tickfont=dict(size=22, color="#363636")
            ),
            yaxis=dict(
                title_font=dict(size=28, color="#363636"),
                tickfont=dict(size=22, color="#363636")
            ),
            margin=dict(t=40, b=100, r=20, l=20),
            title=dict(text=f"Marca: {marca_name}", font=dict(size=24, color="#363636")),
            showlegend=False
        )

        fig.update_layout(**layout_kwargs, **hovermode_layout)
        fig.update_yaxes(automargin=True)
        fig.update_xaxes(automargin=True)
        st.plotly_chart(fig, use_container_width=True)

        seq_cards = color_sequence(palette_name)
        total_produtos = int(dist["quantidade"].sum())
        total_categorias = int(dist["categoria"].nunique())
        _render_summary_cards(
            total_left=total_produtos, label_left="Total de Produtos",
            total_right=total_categorias, label_right="Total de Categorias",
            seq=seq_cards
        )

    # TAB: GRÁFICO DE ROSCA
    with tabs[1]:
        figp = px.pie(
            dist,
            names="categoria", values="quantidade",
            hole=0.55, color="categoria", color_discrete_sequence=seq
        )
        figp.update_traces(
            textposition="inside", textinfo="percent+label",
            textfont=dict(size=28, color="#363636"),
            hovertemplate="<b>%{label}</b><br>Marca: <b>" + marca_name + "</b><br>Quantidade: %{value} (%{percent:.1%})<extra></extra>"
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
            title=dict(text=f"Marca: {marca_name}", font=dict(size=24, color="#363636")),
            hoverlabel=dict(font_size=22, font_color="gray", bgcolor="white", align="left")
        )
        st.plotly_chart(figp, use_container_width=True)

        # Cards (agora usando paleta)
        seq_cards = color_sequence(palette_name)
        total_produtos = int(dist["quantidade"].sum())
        total_categorias = int(dist["categoria"].nunique())
        _render_summary_cards(
            total_left=total_produtos, label_left="Total de Produtos",
            total_right=total_categorias, label_right="Total de Categorias",
            seq=seq_cards
        )

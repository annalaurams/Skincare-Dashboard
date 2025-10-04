# # ui_components/kpi_cards.py
# # -*- coding: utf-8 -*-
# from __future__ import annotations
# import sys
# from typing import Set
# import pandas as pd
# import streamlit as st

# # caminho para os modelos (listas canônicas)
# sys.path.append("/home/usuario/Área de trabalho/Dados/models")
# from ingredient import INGREDIENTES_VALIDOS
# from benefits import BENEFIT_CANONICAL_ORDER
# from category import CATEGORY_CANONICAL_ORDER

# # CSS opcional (mantém o visual dos cards e aumenta UI de tabs/radios)
# st.markdown("""
# <style>
# .stTabs [role="tab"] { font-size: 28px !important; font-weight: 800 !important; padding: 6px 14px !important; }
# .stTabs [role="tab"][aria-selected="true"] { border-bottom: 6px solid currentColor !important; }
# div[data-testid="stWidgetLabel"] p { font-size: 28px !important; font-weight: 800 !important; color: #333 !important; }
# div[role='radiogroup'] label { font-size: 28px !important; font-weight: 800 !important; margin-right: 18px !important; }
# .kpi { border-radius: 18px; padding: 18px 18px 14px 18px; color: white;
#       background: linear-gradient(135deg, var(--card-from), var(--card-to));
#       box-shadow: 0 10px 24px rgba(0,0,0,.12); }
# .kpi .kpi-value { font-size: 1.8rem; font-weight: 800; line-height: 1; }
# .kpi .kpi-label { opacity: .95; font-size: .95rem; }
# </style>
# """, unsafe_allow_html=True)

# def render_kpis(df: pd.DataFrame, show_breakdown: bool = True) -> None:
#     """
#     KPIs globais (sem filtros):
#       - Produtos: nº total de linhas (somando todos os CSVs)
#       - Arquivos: nº de CSVs distintos (coluna _source_file)
#       - Ingredientes: len(INGREDIENTES_VALIDOS)
#       - Benefícios: len(BENEFIT_CANONICAL_ORDER)
#       - Categorias: len(CATEGORY_CANONICAL_ORDER)
#     """
#     c1, c2, c3, c4, c5 = st.columns(5)

#     total_produtos = int(df.shape[0])
#     total_csvs = int(df["_source_file"].nunique()) if "_source_file" in df.columns else 1
#     total_ingredientes = len(INGREDIENTES_VALIDOS)
#     total_beneficios = len(BENEFIT_CANONICAL_ORDER)
#     total_categorias = len(CATEGORY_CANONICAL_ORDER)

#     with c1:
#         st.markdown(
#             f"""
#             <div class="kpi" style="width:250px; padding:15px;">
#                <div class="kpi-value">{total_produtos:,}</div>
#                <div class="kpi-label" style="font-size:16px;">Produtos</div>
#             </div>
#             """.replace(",", "."),
#             unsafe_allow_html=True,
#         )

#     with c2:
#         st.markdown(
#             f"""
#             <div class="kpi" style="width:250px; padding:15px;">
#                <div class="kpi-value">{total_csvs:,}</div>
#                <div class="kpi-label" style="font-size:16px;">Marcas</div>
#             </div>
#             """.replace(",", "."),
#             unsafe_allow_html=True,
#         )

#     with c5:
#         st.markdown(
#             f"""
#             <div class="kpi" style="width:250px; padding:15px;">
#                <div class="kpi-value">{total_ingredientes:,}</div>
#                <div class="kpi-label" style="font-size:16px;">Ingredientes Ativos</div>
#             </div>
#             """.replace(",", "."),
#             unsafe_allow_html=True,
#         )

#     with c4:
#         st.markdown(
#             f"""
#             <div class="kpi" style="width:250px; padding:15px;">
#                <div class="kpi-value">{total_beneficios:,}</div>
#                <div class="kpi-label" style="font-size:16px;">Benefícios </div>
#             </div>
#             """.replace(",", "."),
#             unsafe_allow_html=True,
#         )

#     with c3:
#         st.markdown(
#             f"""
#             <div class="kpi" style="width:250px; padding:15px;">
#                <div class="kpi-value">{total_categorias:,}</div>
#                <div class="kpi-label" style="font-size:16px;">Categorias</div>
#             </div>
#             """.replace(",", "."),
#             unsafe_allow_html=True,
#         )

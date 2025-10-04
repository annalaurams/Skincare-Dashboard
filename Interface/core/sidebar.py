# from __future__ import annotations
# import streamlit as st
# from .colors import PALETTE_OPTIONS
# from .theme import apply_base_theme, apply_palette_css

# def render_sidebar():
#     st.session_state["base_theme"] = "Claro"

#     if "palette_name" not in st.session_state:
#         st.session_state["palette_name"] = PALETTE_OPTIONS[0]

#     with st.sidebar:
#         st.markdown("### 🧪 Skincare Analytics")
#         st.caption("Exploração de dados de produtos cosméticos")
#         st.session_state["palette_name"] = st.selectbox(
#             "Paleta de cores", options=PALETTE_OPTIONS, key="theme_palette"
#         )

#     apply_base_theme()
#     apply_palette_css(st.session_state["palette_name"])

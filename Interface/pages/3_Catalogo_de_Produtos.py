# /home/usuario/Área de trabalho/Dados/Interface/pages/3_Catalogo_de_Produtos.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import math
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

from core.data import load_data
from core.theme import apply_base_theme, apply_palette_css, PALETTE_OPTIONS, color_sequence
from ui_components.filters import pick_categorias, pick_marcas

st.set_page_config(page_title="Skincare • Catálogo de Produtos", page_icon="🛍️", layout="wide")

# ===== Tema =====
if "base_theme" not in st.session_state:
    st.session_state["base_theme"] = "Claro"
if "palette_name" not in st.session_state:
    st.session_state["palette_name"] = PALETTE_OPTIONS[0]
apply_base_theme(st.session_state["base_theme"])
apply_palette_css(st.session_state["palette_name"])
seq = color_sequence(st.session_state["palette_name"])

ROOT = Path(__file__).resolve().parents[1]  # /Interface

# ===== Helpers =====
def brl(x) -> str:
    try:
        return f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"

def split_semicolon(s: str) -> list[str]:
    if not isinstance(s, str) or not s.strip():
        return []
    return [p.strip() for p in s.split(";") if p.strip()]

def cost_per_unit(row):
    try:
        v = float(row.get("quantidade_valor", np.nan))
        p = float(row.get("preco", np.nan))
        u = (row.get("quantidade_unidade") or "").strip()
        if np.isfinite(v) and v > 0 and np.isfinite(p):
            return p / v, u
    except Exception:
        pass
    return None, None

def resolve_image(path: str | None) -> str | None:
    if not isinstance(path, str) or not path.strip():
        return None
    p = path.strip()
    if p.startswith("http://") or p.startswith("https://"):
        return p
    tentative = [
        Path(p), ROOT / p, ROOT / "assets" / p, ROOT / "assets" / "img" / p,
        ROOT / "images" / p, ROOT / "static" / "img" / p, ROOT / "produtos" / p
    ]
    for cand in tentative:
        if cand.exists():
            return str(cand)
    return None

# ===== Dados =====
df = load_data().copy()

# ===== Título =====
st.markdown('<h1 class="themed-title">Catálogo de Produtos</h1>', unsafe_allow_html=True)
st.caption(f"Explore nossa base com {df.shape[0]} produtos de skincare.")

# ===== Filtros =====
st.markdown("### Filtros e Busca")
c0, c1, c2, c3, c4 = st.columns([2,1,1,1,1])
with c0:
    query = st.text_input("🔎 Buscar produtos...", "")
with c1:
    sel_cats = pick_categorias(df, key_prefix="catprod")
with c2:
    sel_marcas = pick_marcas(df, key_prefix="brandprod")
with c3:
    tipos = sorted({tp for s in df["tipo_pele"].dropna() for tp in split_semicolon(s)})
    tipo_sel = st.selectbox("Tipos de pele", ["Todos os tipos"] + tipos, index=0)
with c4:
    ordenacao = st.selectbox(
        "Ordenar",
        ["Nome A–Z", "Nome Z–A", "Preço ↑", "Preço ↓", "Custo por unid ↑", "Custo por unid ↓"],
        index=0
    )

# aplica filtros
df_f = df.copy()
if query.strip():
    q = query.strip().lower()
    df_f = df_f[
        df_f["nome"].str.lower().str.contains(q, na=False) |
        df_f["marca"].str.lower().str.contains(q, na=False) |
        df_f["beneficios"].str.lower().str.contains(q, na=False)
    ]
if sel_cats:
    df_f = df_f[df_f["categoria"].isin(sel_cats)]
if sel_marcas:
    df_f = df_f[df_f["marca"].isin(sel_marcas)]
if tipo_sel != "Todos os tipos":
    df_f = df_f[df_f["tipo_pele"].str.lower().str.contains(tipo_sel.lower(), na=False)]

# custo por unidade para ordenação
if not df_f.empty:
    cp_list, un_list = [], []
    for _, r in df_f.iterrows():
        c, u = cost_per_unit(r)
        cp_list.append(c); un_list.append(u)
    df_f = df_f.assign(_custo=cp_list, _un=un_list)

if ordenacao == "Nome A–Z":
    df_f = df_f.sort_values("nome")
elif ordenacao == "Nome Z–A":
    df_f = df_f.sort_values("nome", ascending=False)
elif ordenacao == "Preço ↑":
    df_f = df_f.sort_values("preco", na_position="last")
elif ordenacao == "Preço ↓":
    df_f = df_f.sort_values("preco", ascending=False, na_position="last")
elif ordenacao == "Custo por unid ↑":
    df_f = df_f.sort_values("_custo", na_position="last")
else:
    df_f = df_f.sort_values("_custo", ascending=False, na_position="last")

st.markdown(f"Mostrando **{df_f.shape[0]}** de {df.shape[0]} produtos")

# ===== Estilos (informações maiores + pílulas coloridas) =====
st.markdown(f"""
<style>
.prod-card {{
  border:1px solid #e8e7ef; border-radius:18px; overflow:hidden;
  background: linear-gradient(135deg,{seq[0]}22,{seq[1]}11);
}}
.prod-head {{
  height:180px; display:flex; align-items:center; justify-content:center;
  background:linear-gradient(160deg,{seq[0]}33,{seq[1]}29);
}}
.prod-footer {{ padding:12px 16px 18px 16px; }}
.prod-name {{ font-size:18px; font-weight:800; line-height:1.25; }}
.prod-brand {{ font-size:13px; opacity:.8; margin-top:2px; }}
.prod-price {{ font-size:18px; font-weight:800; color:{seq[0]}; margin-top:6px; }}
.prod-cpu {{ font-size:13px; opacity:.8; margin-top:2px; }}

.pill {{ display:inline-flex; align-items:center; gap:.4rem;
        padding:4px 10px; border-radius:999px; font-size:12px;
        border:1px solid transparent; }}
.pill.skin {{ background:{seq[0]}22; color:#111; border-color:{seq[0]}; }}
.pill.benefit {{ background:{seq[1]}22; color:#111; border-color:{seq[1]}; }}
.pill + .pill {{ margin-left:6px; }}
.pills {{ margin-top:8px; display:flex; flex-wrap:wrap; gap:6px; }}
</style>
""", unsafe_allow_html=True)

# ===== Grid de cards =====
if df_f.empty:
    st.info("Nenhum produto encontrado para os filtros atuais.")
else:
    cols_per_row = 3
    rows = math.ceil(df_f.shape[0] / cols_per_row)
    items = df_f.reset_index(drop=True)

    for r in range(rows):
        cols = st.columns(cols_per_row)
        for c in range(cols_per_row):
            idx = r*cols_per_row + c
            if idx >= items.shape[0]:
                break
            row = items.iloc[idx]
            with cols[c]:
                st.markdown('<div class="prod-card">', unsafe_allow_html=True)

                # Cabeçalho / imagem
                img_path = resolve_image(row.get("imagem", ""))
                st.markdown('<div class="prod-head">', unsafe_allow_html=True)
                if img_path:
                    st.image(img_path, width=150)
                else:
                    st.markdown('<span style="opacity:.6;">(sem imagem)</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Conteúdo
                st.markdown('<div class="prod-footer">', unsafe_allow_html=True)
                st.markdown(f"<div class='prod-name'>{row['nome']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='prod-brand'>{row['marca']}</div>", unsafe_allow_html=True)

                price = brl(row["preco"])
                c_u, u = cost_per_unit(row)
                st.markdown(f"<div class='prod-price'>{price}</div>", unsafe_allow_html=True)
                if c_u is not None and u:
                    st.markdown(f"<div class='prod-cpu'>{brl(c_u)}/{u}</div>", unsafe_allow_html=True)

                # Pílulas coloridas: tipos de pele e benefícios (até 2 de cada)
                tipos = split_semicolon(row.get("tipo_pele",""))[:2]
                bens  = split_semicolon(row.get("beneficios",""))[:2]
                pills_html = (
                    "".join([f"<span class='pill skin'>{t}</span>" for t in tipos]) +
                    "".join([f"<span class='pill benefit'>{b}</span>" for b in bens])
                )
                if pills_html:
                    st.markdown(f"<div class='pills'>{pills_html}</div>", unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)  # /prod-footer
                st.markdown('</div>', unsafe_allow_html=True)  # /prod-card

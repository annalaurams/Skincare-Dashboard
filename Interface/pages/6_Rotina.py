# /home/usuario/Área de trabalho/Dados/Interface/pages/6_Rotina.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import math
import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

from core.data import load_data
from core.theme import apply_base_theme, apply_palette_css, PALETTE_OPTIONS, color_sequence

# ===================== Config =====================
st.set_page_config(page_title="Skincare • Montagem de Rotina", page_icon="🧴", layout="wide")

if "base_theme" not in st.session_state:
    st.session_state["base_theme"] = "Claro"
if "palette_name" not in st.session_state:
    st.session_state["palette_name"] = PALETTE_OPTIONS[0]
apply_base_theme(st.session_state["base_theme"])
apply_palette_css(st.session_state["palette_name"])
seq = color_sequence(st.session_state["palette_name"])

# ===================== Helpers =====================
def brl(x):
    try:
        return f"R$ {float(x):.2f}".replace(".", ",")
    except Exception:
        return "—"

def split_semicolon(s: str) -> list[str]:
    if not isinstance(s, str) or not s.strip():
        return []
    return [p.strip() for p in s.split(";") if p.strip()]

def match_any(text: str, tokens: list[str]) -> int:
    """Conta quantos tokens aparecem no texto (case-insensitive)."""
    if not tokens:
        return 0
    t = (text or "").lower()
    return sum(1 for tok in tokens if tok.lower() in t)

# mapeamento simples de categorias em "grupos de rotina"
CAT_MAP = {
    "limpeza": ["limpeza", "sabonete", "cleanser", "gel de limpeza"],
    "hidratante": ["hidratante", "creme", "loção", "locao", "moistur", "balm"],
    "protetor solar": ["protetor solar", "proteção solar", "fps", "sunscreen"],
    "sérum": ["sérum", "serum", "essência", "tonico", "tônico", "ampoule"],
    "tratamento": ["tratamento", "antiacne", "acne", "manchas", "retinol", "anti-idade", "clareador"],
    # você pode estender conforme sua taxonomia
}

DEFAULT_MORNING = ["limpeza", "sérum", "hidratante", "protetor solar"]
DEFAULT_NIGHT   = ["limpeza", "tratamento", "hidratante"]

def infer_group(categoria: str) -> str | None:
    c = (categoria or "").lower()
    for g, keys in CAT_MAP.items():
        if any(k in c for k in keys):
            return g
    return None

def score_product(row, wanted_bens: list[str], wanted_ings: list[str]) -> float:
    """Score simples para priorizar produtos aderentes às preferências."""
    bens = row.get("beneficios", "") or ""
    ings = row.get("ingredientes", "") or ""
    s = 0.0
    s += 2.0 * match_any(bens, wanted_bens)
    s += 1.5 * match_any(ings, wanted_ings)
    # leve bônus para preço mais baixo (normalizado)
    try:
        p = float(row.get("preco", np.nan))
        if math.isfinite(p):
            s += 0.5 * (1.0 / (1.0 + p/100.0))
    except Exception:
        pass
    return s

# ===================== Data =====================
df = load_data().copy()
df["group"] = df["categoria"].apply(infer_group)

# coleções auxiliares
tipos_pele_unicos = sorted({tp.strip() for s in df.get("tipo_pele", pd.Series(dtype=str)).dropna() for tp in split_semicolon(s)})
beneficios_unicos = sorted({b.strip() for s in df.get("beneficios", pd.Series(dtype=str)).dropna() for b in split_semicolon(s)})
ingredientes_unicos = sorted({i.strip() for s in df.get("ingredientes", pd.Series(dtype=str)).dropna() for i in split_semicolon(s)})

st.markdown('<h1 class="themed-title">Montagem de Rotina</h1>', unsafe_allow_html=True)
st.caption("Crie uma rotina personalizada baseada no seu tipo de pele e necessidades.")

# ===================== UI — Formulário =====================
left, right = st.columns([3,1])

with left:
    st.markdown("#### 1. Qual é o seu tipo de pele?")
    tp_sel = st.selectbox("Selecione seu tipo de pele", [""] + tipos_pele_unicos, index=0, label_visibility="collapsed")

    st.markdown("#### 2. Quais são suas principais preocupações?")
    cols = st.columns(2)
    with cols[0]:
        opts1 = ["Hidratação", "Controle de oleosidade", "Sensibilidade", "Poros dilatados"]
    with cols[1]:
        opts2 = ["Anti-idade", "Uniformização do tom", "Acne", "Manchas"]
    ben_checks = []
    for o in opts1:
        if st.checkbox(o, key=f"b1_{o}"):
            ben_checks.append(o)
    for o in opts2:
        if st.checkbox(o, key=f"b2_{o}"):
            ben_checks.append(o)

    st.markdown("#### 3. Qual é o seu orçamento?")
    min_p = max(20, float(df["preco"].min(skipna=True) or 20))
    max_p = float(df["preco"].max(skipna=True) or 500)
    budget = st.slider("", min_value=50, max_value=int(max(100, max_p)), value=200, step=10, format="R$ %d")
    st.caption(f"Orçamento total para a rotina completa: **{brl(budget)}**")

    st.markdown("#### 4. Ingredientes de preferência (opcional)")
    ing_sel = st.multiselect("", ingredientes_unicos, max_selections=8)

    st.markdown("#### 5. Categorias da rotina (opcional)")
    all_groups = list(CAT_MAP.keys())
    groups_sel = st.multiselect("Deixe em branco para usar o padrão (manhã e noite)", all_groups)

with right:
    st.markdown("#### Resumo da Configuração")
    st.markdown(f"- **Tipo de pele:** {tp_sel or 'Não selecionado'}")
    st.markdown(f"- **Preocupações:** {', '.join(ben_checks) if ben_checks else '—'}")
    st.markdown(f"- **Orçamento:** {brl(budget)}")
    st.markdown(f"- **Ingredientes:** {', '.join(ing_sel) if ing_sel else '—'}")
    st.markdown(f"- **Categorias:** {', '.join(groups_sel) if groups_sel else 'Padrão (manhã/noite)'}")

st.markdown("---")
generate = st.button("🧪 Gerar Rotina Personalizada", use_container_width=True, type="primary")

# ===================== Lógica de geração =====================
if generate:
    # filtra por tipo de pele (quando marcado no registro do produto)
    df_use = df.copy()
    if tp_sel:
        def has_tp(s: str) -> bool:
            return tp_sel.lower() in (s or "").lower()
        df_use = df_use[df_use["tipo_pele"].apply(has_tp)]

    # constrói lista de grupos-alvo
    morning = groups_sel or DEFAULT_MORNING
    night   = groups_sel or DEFAULT_NIGHT

    # candidatos por grupo com score
    df_use["score"] = df_use.apply(lambda r: score_product(r, ben_checks, ing_sel), axis=1)
    # mínimo: respeitar grupo inferido
    candidates = {g: df_use[df_use["group"] == g].sort_values(["score","preco"], ascending=[False, True]) for g in set(morning+night)}

    def greedy_pick(target_groups, budget_left):
        picks = []
        for g in target_groups:
            cand = candidates.get(g, pd.DataFrame())
            if cand.empty:
                continue
            # pega o melhor que caiba no orçamento; se nenhum cabe, pega o mais barato (e marcamos extrapolo)
            chosen = cand[cand["preco"] <= budget_left].head(1)
            extrapolo = False
            if chosen.empty:
                chosen = cand.head(1)
                extrapolo = True
            row = chosen.iloc[0].to_dict()
            row["_group"] = g
            row["_exceed"] = extrapolo and (row.get("preco",0) > budget_left)
            picks.append(row)
            budget_left -= float(row.get("preco", 0))
            if budget_left < 0:
                budget_left = 0
        return picks

    morning_picks = greedy_pick(morning, budget_left=budget)
    spent_morning = sum(p.get("preco",0) for p in morning_picks)
    night_picks   = greedy_pick(night, budget_left=max(0, budget - spent_morning))

    final_picks = morning_picks + night_picks
    total_cost = sum(p.get("preco",0) for p in final_picks)
    distinct_benefits = set()
    for p in final_picks:
        distinct_benefits.update(split_semicolon(str(p.get("beneficios",""))))

    # alerta se extrapolou
    if total_cost > budget:
        st.warning(f"⚠️ A rotina proposta ultrapassa o orçamento em **{brl(total_cost - budget)}**. "
                   "Você pode reduzir o orçamento ou remover categorias.")

    # ===================== Header KPIs =====================
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Custo Total", brl(total_cost))
    with k2:
        st.metric("Produtos", f"{len(final_picks)}")
    with k3:
        st.metric("Benefícios (únicos)", f"{len(distinct_benefits)}")
    with k4:
        st.metric("Orçamento", brl(budget))

    # ===================== Listas (manhã/noite) =====================
    st.markdown("### Rotina Matinal")
    if not morning_picks:
        st.info("Não foi possível montar itens para a manhã com os filtros atuais.")
    else:
        for idx, p in enumerate(morning_picks, 1):
            with st.container(border=True):
                col1, col2, col3 = st.columns([6,2,2])
                with col1:
                    st.markdown(f"**{idx}. {p.get('_group','').capitalize()}**  \n{p.get('nome','—')} - {p.get('marca','')}")
                    tags = [t.strip() for t in split_semicolon(str(p.get('beneficios','')))[:3] if t.strip()]
                    if tags:
                        st.markdown(" ".join([f"<span style='background:#eef;border:1px solid #dde;border-radius:999px;padding:2px 8px;margin-right:6px;'>{t}</span>" for t in tags]), unsafe_allow_html=True)
                with col2:
                    st.markdown(brl(p.get("preco","—")))
                with col3:
                    st.markdown(p.get("quantidade","—"))
                if p.get("_exceed"):
                    st.caption("⚠️ Item selecionado extrapola o orçamento disponível no passo.")

    st.markdown("### Rotina Noturna")
    if not night_picks:
        st.info("Não foi possível montar itens para a noite com os filtros atuais.")
    else:
        for idx, p in enumerate(night_picks, 1):
            with st.container(border=True):
                col1, col2, col3 = st.columns([6,2,2])
                with col1:
                    st.markdown(f"**{idx}. {p.get('_group','').capitalize()}**  \n{p.get('nome','—')} - {p.get('marca','')}")
                    tags = [t.strip() for t in split_semicolon(str(p.get('beneficios','')))[:3] if t.strip()]
                    if tags:
                        st.markdown(" ".join([f"<span style='background:#eef;border:1px solid #dde;border-radius:999px;padding:2px 8px;margin-right:6px;'>{t}</span>" for t in tags]), unsafe_allow_html=True)
                with col2:
                    st.markdown(brl(p.get("preco","—")))
                with col3:
                    st.markdown(p.get("quantidade","—"))
                if p.get("_exceed"):
                    st.caption("⚠️ Item selecionado extrapola o orçamento disponível no passo.")

    # ===================== Tabela de candidatos (opcional) =====================
    st.markdown("---")
    st.subheader("Produtos candidatos usados na seleção")
    show_cols = ["nome","marca","categoria","preco","beneficios","ingredientes"]
    cand_df = pd.concat([candidates[g] for g in candidates]).drop_duplicates(subset=["nome"])
    cand_df = cand_df[show_cols + ["group","score"]].rename(columns={"group":"grupo"})
    st.dataframe(cand_df, use_container_width=True)
else:
    st.info("Preencha as informações e clique em **Gerar Rotina Personalizada** para ver a sugestão de manhã/noite.")

# /home/usuario/Área de trabalho/Dados/Interface/pages/6_Produtos.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import sys, re, base64
from pathlib import Path
from typing import List, Optional
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from core.data import load_data
from core.theme import apply_base_theme, apply_palette_css, color_sequence

# ============ CONFIG ============
st.set_page_config(page_title="Skincare • Produtos", page_icon="🧴", layout="wide")

# ✅ Defina explicitamente a pasta de imagens (ajusta se mudar a estrutura)
IMAGES_ROOT = Path("/home/usuario/Área de trabalho/Dados/imagens")
USE_LOCAL_IMAGES = True  # coloque False para testar sem imagens

# ============ MODELS (ordem canônica) ============
sys.path.append("/home/usuario/Área de trabalho/Dados/models")
try:
    from category import CATEGORY_CANONICAL_ORDER
except Exception:
    CATEGORY_CANONICAL_ORDER = None

# ============ TEMA / PALETA ============
if "palette_name" not in st.session_state:
    st.session_state["palette_name"] = "Roxo & Rosa"
apply_base_theme()
apply_palette_css(st.session_state["palette_name"])
SEQ = color_sequence(st.session_state["palette_name"])

def accent(i: int = 0) -> str: return SEQ[i % len(SEQ)] if SEQ else "#6e56cf"
def text_color() -> str:       return "#262730"
def subtext_color() -> str:    return "#555"
def panel_bg() -> str:         return "#ffffff"
def neutral_border() -> str:   return "#ececf1"

# ============ PARÂMETROS EDITÁVEIS ============
TITLE_TEXT, TITLE_SIZE = "Produtos de Skincare", 52
TAGLINE_TEXT, TAGLINE_SIZE = "Visualize os produtos disponíveis e explore por marca e categoria.", 20

FILTER_TITLE_PX, FILTER_LABEL_PX, FILTER_INPUT_PX = 26, 18, 18

SUMMARY_CARD_H, SUMMARY_RADIUS = 110, 14
SUMMARY_SHADOW, SUMMARY_TITLE_PX, SUMMARY_VALUE_PX = "0 10px 28px rgba(0,0,0,.08)", 14, 28

GRID_GAP, CARD_RADIUS, CARD_PAD = 18, 16, "14px 16px"
CARD_SHADOW, IMG_BOX = "0 10px 28px rgba(0,0,0,.08)", 110
NAME_PX, META_PX, PRICE_PX, LIST_TEXT_PX = 18, 14, 18, 14
MAX_ING_SHOW, MAX_BEN_SHOW, MAX_SKIN_SHOW = 4, 3, 3

# ============ HELPERS ============
def split_semicolon(s: str) -> List[str]:
    if not isinstance(s, str) or not s.strip(): return []
    return [p.strip() for p in s.split(";") if p.strip()]

def brl(x) -> str:
    try:
        if pd.isna(x): return "—"
        return f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"

def qty_text(row: pd.Series) -> str:
    q, qv, qu = row.get("quantidade"), row.get("quantidade_valor"), row.get("quantidade_unidade")
    if isinstance(q, str) and q.strip(): return q
    if pd.notna(qv) and isinstance(qu, str) and qu.strip():
        try: return f"{float(qv):g}{qu}"
        except Exception: return f"{qv}{qu}"
    return "—"

def order_categories_list(raw: List[str]) -> List[str]:
    if not raw: return []
    if CATEGORY_CANONICAL_ORDER:
        canon = [c for c in CATEGORY_CANONICAL_ORDER if c in raw]
        extra = [c for c in raw if c not in canon]
        return canon + sorted(extra)
    return sorted(raw)

def slugify(s: str) -> str:
    s = re.sub(r"[^\w\s-]", "", str(s).lower())
    return re.sub(r"\s+", "-", s).strip("-")

def file_to_data_uri(path: Path) -> Optional[str]:
    try:
        if not path.exists() or not path.is_file(): return None
        mime = "image/png" if path.suffix.lower()==".png" else "image/jpeg"
        b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
        return f"data:{mime};base64,{b64}"
    except Exception:
        return None

def guess_images_root(csv_hint: Optional[str]) -> Path:
    """
    Ordem de busca:
      1) IMAGES_ROOT explícito (acima)
      2) <dir_da_página>/../imagens  -> /.../Dados/imagens
      3) CWD/imagens
    """
    if IMAGES_ROOT.exists():
        return IMAGES_ROOT
    try:
        p = Path(__file__).resolve().parent.parent / "imagens"
        if p.exists(): return p
    except Exception:
        pass
    p2 = Path.cwd() / "imagens"
    return p2

def infer_local_image(row: pd.Series) -> Optional[str]:
    """Prioriza NOME DO ARQUIVO vindo do CSV. Depois tenta pelo slug do produto."""
    if not USE_LOCAL_IMAGES: return None

    # URL completa já serve
    for k in ["image_url", "imagem_url", "url_imagem"]:
        val = row.get(k)
        if isinstance(val, str) and val.strip() and val.startswith(("http://", "https://")):
            return val

    images_root = guess_images_root(row.get("_source_file"))
    brand = str(row.get("marca") or "").strip().lower().replace(" ", "_")
    brand_dir = images_root / brand

    # Aceita uma lista BEM ampla de possíveis nomes de coluna para arquivo da imagem
    img_cols = [
        "imagem", "image_filename", "arquivo_imagem", "foto", "img", "image",
        "nome_imagem", "imagem_nome", "arquivo", "filename"
    ]

    # 1) Nome do arquivo informado no CSV (PRIORIDADE MÁXIMA)
    for k in img_cols:
        val = row.get(k)
        if isinstance(val, str) and val.strip() and not val.startswith(("http://", "https://")):
            fn = Path(val).name
            candidates = [brand_dir / fn, images_root / fn]
            if not Path(fn).suffix:
                for ext in (".jpg", ".jpeg", ".png", ".webp"):
                    candidates += [brand_dir / f"{fn}{ext}", images_root / f"{fn}{ext}"]
            for c in candidates:
                uri = file_to_data_uri(c)
                if uri: return uri

    # 2) Fallback pelo NOME DO PRODUTO
    prod_slug = slugify(row.get("nome", ""))
    if prod_slug:
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            uri = file_to_data_uri(brand_dir / f"{prod_slug}{ext}")
            if uri: return uri
    return None

# ============ CSS ============
st.markdown(f"""
<style>
  .page-title {{ margin:0; font-size:{TITLE_SIZE}px; color:{accent(0)}; }}
  .page-subtitle {{ margin:.35rem 0 1.0rem 0; color:{subtext_color()}; font-size:{TAGLINE_SIZE}px; }}

  .filters {{
    border:1px solid {neutral_border()}; border-radius:14px; background:{panel_bg()};
    box-shadow:0 8px 24px rgba(0,0,0,.06); padding:14px;
  }}
  .filters h3 {{ margin:0 0 .5rem 0; font-size:{FILTER_TITLE_PX}px; color:{text_color()}; }}

  .stSelectbox label, .stMultiSelect label, .stTextInput label {{
    font-size:{FILTER_LABEL_PX}px !important; color:{text_color()} !important; font-weight:700 !important;
  }}
  .stSelectbox div[data-baseweb="select"] input,
  .stMultiSelect div[data-baseweb="select"] input,
  .stTextInput input {{ font-size:{FILTER_INPUT_PX}px !important; }}
  .stSelectbox, .stMultiSelect, .stTextInput {{ margin-bottom: .35rem !important; }}

  .summary {{
    border:1px solid {neutral_border()}; border-radius:{SUMMARY_RADIUS}px; background:{panel_bg()};
    box-shadow:{SUMMARY_SHADOW}; padding:12px 14px; height:{SUMMARY_CARD_H}px;
    display:flex; flex-direction:column; justify-content:center; gap:.25rem;
  }}
  .summary .t {{ font-size:{SUMMARY_TITLE_PX}px; color:{subtext_color()}; font-weight:700; }}
  .summary .v {{ font-size:{SUMMARY_VALUE_PX}px; color:{text_color()}; font-weight:900; line-height:1; }}

  .grid {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap:{GRID_GAP}px; padding:4px; }}
  .card {{ border:1px solid {neutral_border()}; border-radius:{CARD_RADIUS}px; background:{panel_bg()};
          box-shadow:{CARD_SHADOW}; overflow:hidden; display:flex; flex-direction:column;
          transition: transform .12s ease, box-shadow .12s ease; }}
  .card:hover {{ transform: translateY(-3px); box-shadow:0 14px 32px rgba(0,0,0,.10); }}
  .top {{ background:linear-gradient(135deg,{accent(0)}15,{accent(1)}10); height:150px; display:flex; align-items:center; justify-content:center; padding:10px; }}
  .imgbox {{ width:{IMG_BOX}px; height:{IMG_BOX}px; background:{panel_bg()}; border-radius:14px; display:flex; align-items:center; justify-content:center;
             overflow:hidden; box-shadow: inset 0 0 0 1px {neutral_border()}; }}
  .imgbox img {{ max-width:100%; max-height:100%; object-fit:contain; }}
  .noimg {{ font-size:12px; opacity:.6; text-align:center; color:{subtext_color()}; }}
  .body {{ padding:{CARD_PAD}; display:flex; flex-direction:column; gap:.45rem; flex-grow:1; }}
  .name {{ font-weight:900; font-size:{NAME_PX}px; color:{text_color()}; line-height:1.25; }}
  .meta {{ color:{subtext_color()}; font-size:{META_PX}px; }}
  .price {{ font-weight:900; color:{accent(0)}; font-size:{PRICE_PX}px; }}
  .list {{ font-size:{LIST_TEXT_PX}px; color:{text_color()}; line-height:1.4; }}
  details {{ margin-top:auto; }}
  details summary {{ font-weight:700; color:{accent(0)}; cursor:pointer; list-style:none; padding:8px 0; user-select:none; }}
  details summary::-webkit-details-marker {{ display:none; }}
  details summary::before {{ content:"▶ "; display:inline-block; transition:transform .2s; }}
  details[open] summary::before {{ transform:rotate(90deg); }}
  details > div {{ padding-top:.5rem; border-top:1px solid {neutral_border()}; }}
</style>
""", unsafe_allow_html=True)

# ============ TÍTULO ============
st.markdown(f"<h1 class='page-title'>{TITLE_TEXT}</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='page-subtitle'>{TAGLINE_TEXT}</div>", unsafe_allow_html=True)

# ============ DADOS ============
df = load_data()
if df is None or df.empty:
    st.info("Sem dados para exibir.")
    st.stop()

# ============ SESSION STATE ============
brands_all = sorted(df["marca"].dropna().unique().tolist())
cats_present = sorted(df["categoria"].dropna().unique().tolist())
cats_all = order_categories_list(cats_present)
if "flt_prod_brands" not in st.session_state: st.session_state["flt_prod_brands"] = brands_all
if "flt_prod_cats" not in st.session_state:   st.session_state["flt_prod_cats"] = cats_all

# ============ FILTROS (mesmo tamanho/linha) ============
st.markdown("<div class='filters'><h3>Filtros e Busca</h3>", unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns([1.4, 1, 1, 1, .7])
with c1:
    q_text = st.text_input("🔍 Buscar produtos…", "", key="search_text")
with c2:
    sel_cats = st.multiselect("📂 Categoria", options=cats_all,
                              default=st.session_state["flt_prod_cats"], key="flt_prod_cats")
with c3:
    sel_brands = st.multiselect("🏷️ Marca", options=brands_all,
                                default=st.session_state["flt_prod_brands"], key="flt_prod_brands")
with c4:
    order = st.selectbox("⚙️ Ordenar por",
                         ["Relevância", "Preço (↑)", "Preço (↓)", "Quantidade (↑)", "Quantidade (↓)",
                          "Nome (A–Z)", "Nome (Z–A)"], index=0)
with c5:
    if st.button("🔄 Mostrar todos", use_container_width=True):
        st.session_state["flt_prod_brands"] = brands_all
        st.session_state["flt_prod_cats"] = cats_all
        st.session_state["search_text"] = ""
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)

# ============ FILTRAGEM ============
df_f = df.copy()
if sel_brands: df_f = df_f[df_f["marca"].isin(sel_brands)]
if sel_cats:   df_f = df_f[df_f["categoria"].isin(sel_cats)]
if q_text.strip():
    ql = q_text.lower()
    def _hit(r):
        return any(ql in str(r.get(col, "")).lower() for col in ["nome","ingredientes","beneficios"])
    df_f = df_f[df_f.apply(_hit, axis=1)]

# ============ ORDENAÇÃO ============
def safe_float(x):
    try: return float(x)
    except Exception: return float("nan")

if order == "Preço (↑)":
    df_f = df_f.sort_values("preco", na_position="last")
elif order == "Preço (↓)":
    df_f = df_f.sort_values("preco", ascending=False, na_position="last")
elif order == "Quantidade (↑)":
    aux = df_f["quantidade_valor"] if "quantidade_valor" in df_f.columns else df_f["quantidade"].apply(
        lambda s: safe_float(re.findall(r"[\d\.,]+", str(s).replace(",", "."))[0]) if re.findall(r"[\d\.,]+", str(s).replace(",", ".")) else float("nan"))
    df_f = df_f.assign(_q=aux).sort_values("_q", na_position="last").drop(columns=["_q"])
elif order == "Quantidade (↓)":
    aux = df_f["quantidade_valor"] if "quantidade_valor" in df_f.columns else df_f["quantidade"].apply(
        lambda s: safe_float(re.findall(r"[\d\.,]+", str(s).replace(",", "."))[0]) if re.findall(r"[\d\.,]+", str(s).replace(",", ".")) else float("nan"))
    df_f = df_f.assign(_q=aux).sort_values("_q", ascending=False, na_position="last").drop(columns=["_q"])
elif order == "Nome (A–Z)":
    df_f = df_f.sort_values("nome", na_position="last")
elif order == "Nome (Z–A)":
    df_f = df_f.sort_values("nome", ascending=False, na_position="last")

# ============ RESUMO ============
n_prod = int(df_f["nome"].nunique())
preco_medio = df_f["preco"].mean() if "preco" in df_f.columns else float("nan")

s1, s2, s3 = st.columns([1,1,2])
with s1:
    st.markdown(f"<div class='summary'><div class='t'>Produtos listados</div><div class='v'>{n_prod}</div></div>", unsafe_allow_html=True)
with s2:
    st.markdown(f"<div class='summary'><div class='t'>Preço médio</div><div class='v'>{brl(preco_medio)}</div></div>", unsafe_allow_html=True)
with s3:
    st.markdown(f"<div class='summary'><div class='t'>Filtros ativos</div><div class='v' style='font-size:16px;'>{len(sel_brands)} marca(s) • {len(sel_cats)} categoria(s)</div></div>", unsafe_allow_html=True)

st.markdown("---")

if df_f.empty:
    st.info("Nenhum produto encontrado com os filtros atuais.")
    st.stop()

# ============ PREPARA VIEW ============
def pick_top(items: List[str], max_n: int) -> List[str]:
    out = []
    for v in items:
        if v and v not in out: out.append(v)
        if len(out) >= max_n: break
    return out

rows = []
for _, r in df_f.iterrows():
    ings = split_semicolon(r.get("ingredientes", ""))
    bens = split_semicolon(r.get("beneficios", ""))
    skins = split_semicolon(r.get("tipo_pele", ""))
    img_uri = infer_local_image(r) if USE_LOCAL_IMAGES else None

    rows.append({
        "nome": r.get("nome"),
        "marca": r.get("marca"),
        "categoria": r.get("categoria"),
        "preco_fmt": brl(r.get("preco")),
        "quantidade_txt": qty_text(r),
        "ingredientes_resumo": "; ".join(pick_top(ings, MAX_ING_SHOW)) if ings else "—",
        "beneficios_resumo": "; ".join(pick_top(bens, MAX_BEN_SHOW)) if bens else "—",
        "tipo_pele_resumo": "; ".join(pick_top(skins, MAX_SKIN_SHOW)) if skins else "—",
        "ingredientes_full": "; ".join(ings) if ings else "—",
        "beneficios_full": "; ".join(bens) if bens else "—",
        "tipo_pele_full": "; ".join(skins) if skins else "—",
        "image_uri": img_uri
    })
view = pd.DataFrame(rows)

# ============ CARDS ============
cards = []
for _, r in view.iterrows():
    nome = str(r['nome']).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    marca = str(r['marca']).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    categoria = str(r['categoria'] or "—").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    if isinstance(r["image_uri"], str) and r["image_uri"]:
        img_html = f"<img src='{r['image_uri']}' alt='{nome}'/>"
    else:
        img_html = "<span class='noimg'>📷<br>sem imagem</span>"

    det = f"""
    <div class="list"><b>Ingredientes (completos):</b><br>{r['ingredientes_full']}</div>
    <div class="list" style="margin-top:0.5rem;"><b>Benefícios (completos):</b><br>{r['beneficios_full']}</div>
    <div class="list" style="margin-top:0.5rem;"><b>Tipo de pele (completo):</b><br>{r['tipo_pele_full']}</div>
    """

    cards.append(f"""
    <div class="card">
      <div class="top"><div class="imgbox">{img_html}</div></div>
      <div class="body">
        <div class="name">{nome}</div>
        <div class="meta">{marca} • {categoria}</div>
        <div style="display:flex; gap:10px; align-items:baseline; flex-wrap:wrap; margin:0.3rem 0;">
          <div class="price">{r['preco_fmt']}</div>
          <div class="meta">{r['quantidade_txt']}</div>
        </div>
        <div class="list"><b>Ativos:</b> {r['ingredientes_resumo']}</div>
        <div class="list"><b>Benefícios:</b> {r['beneficios_resumo']}</div>
        <div class="list"><b>Tipo de pele:</b> {r['tipo_pele_resumo']}</div>
        <details><summary>Ver detalhes completos</summary><div>{det}</div></details>
      </div>
    </div>
    """)

html = f"""
<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body {{ margin:0; padding:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; background:transparent; }}
  .grid {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap:{GRID_GAP}px; }}
  .card {{ border:1px solid {neutral_border()}; border-radius:{CARD_RADIUS}px; background:{panel_bg()};
          box-shadow:{CARD_SHADOW}; overflow:hidden; display:flex; flex-direction:column; }}
  .card:hover {{ transform: translateY(-3px); box-shadow:0 14px 32px rgba(0,0,0,.10); transition:.12s; }}
  .top {{ background:linear-gradient(135deg,{accent(0)}15,{accent(1)}10); height:150px; display:flex; align-items:center; justify-content:center; padding:10px; }}
  .imgbox {{ width:{IMG_BOX}px; height:{IMG_BOX}px; background:{panel_bg()}; border-radius:14px; display:flex; align-items:center; justify-content:center;
            overflow:hidden; box-shadow: inset 0 0 0 1px {neutral_border()}; }}
  .imgbox img {{ max-width:100%; max-height:100%; object-fit:contain; }}
  .noimg {{ font-size:12px; opacity:.6; text-align:center; color:{subtext_color()}; }}
  .body {{ padding:{CARD_PAD}; display:flex; flex-direction:column; gap:.45rem; flex-grow:1; }}
  .name {{ font-weight:900; font-size:{NAME_PX}px; color:{text_color()}; line-height:1.25; }}
  .meta {{ color:{subtext_color()}; font-size:{META_PX}px; }}
  .price {{ font-weight:900; color:{accent(0)}; font-size:{PRICE_PX}px; }}
  .list {{ font-size:{LIST_TEXT_PX}px; color:{text_color()}; line-height:1.4; }}
  details {{ margin-top:auto; }}
  details summary {{ font-weight:700; color:{accent(0)}; cursor:pointer; list-style:none; padding:8px 0; user-select:none; }}
  details summary::-webkit-details-marker {{ display:none; }}
  details summary::before {{ content:"▶ "; display:inline-block; transition:transform .2s; }}
  details[open] summary::before {{ transform:rotate(90deg); }}
  details > div {{ padding-top:.5rem; border-top:1px solid {neutral_border()}; }}
</style>
</head>
<body>
  <div class="grid">{''.join(cards)}</div>
</body></html>
"""
estimated_height = max(900, min(4000, int(len(view) * 160)))
components.html(html, height=estimated_height, scrolling=True)

from include import *

st.markdown("""
<style>
.stTabs [role="tab"] { font-size: 28px !important; font-weight: 800 !important; padding: 6px 14px !important; }
.stTabs [role="tab"][aria-selected="true"] { border-bottom: 6px solid currentColor !important; }

div[data-testid="stWidgetLabel"] p { font-size: 28px !important; font-weight: 800 !important; color: #333 !important; }
div[role='radiogroup'] label { font-size: 28px !important; font-weight: 800 !important; margin-right: 18px !important; }

.kpi {
  border-radius: 18px;
  padding: 18px 18px 14px 18px;
  color: white;
  background: linear-gradient(135deg, var(--card-from), var(--card-to));
  box-shadow: 0 10px 24px rgba(0,0,0,.12);
}
.kpi .kpi-value { font-size: 1.8rem; font-weight: 800; line-height: 1; }
.kpi .kpi-label { opacity: .95; font-size: .95rem; }
</style>
""", unsafe_allow_html=True)

#  Helpers 
def _split_semicolon(s: str) -> list[str]:
    if not isinstance(s, str) or not s.strip():
        return []
    return [p.strip() for p in s.split(";") if p.strip()]

def _to_base_types(raw: str) -> list[str]:

    s = str(raw or "").lower()
    if not s:
        return []

    if SKIN_TYPE_SYNONYMS_PT:
        found = set()
        for canonical, syns in SKIN_TYPE_SYNONYMS_PT.items():
            for term in syns:
                if term and term.lower() in s:
                    found.add(canonical.lower())
                    break
        if "todos" in s and "tipo" in s:
            found.add("todos os tipos")
        return list(found) if found else ["(não informado)"]

    tokens = _split_semicolon(s)
    return tokens if tokens else ["(não informado)"]

def _count_unique_skin_types(df: pd.DataFrame) -> int:
    if "tipo_pele" not in df.columns:
        return 0
    unique_set = set()
    for raw in df["tipo_pele"]:
        for b in _to_base_types(raw):
            unique_set.add(b)

    if SKIN_TYPE_CANONICAL_ORDER:
        can_set = {x.lower() for x in SKIN_TYPE_CANONICAL_ORDER}
        unique_set = {t for t in unique_set if t in can_set or t == "(não informado)"}

    return len(unique_set)

#  Render 
def render_kpis(df: pd.DataFrame, show_breakdown: bool = True) -> None:
    """
      - Produtos: nº total de linhas
      - Marcas: nº de CSVs distintos (via _source_file) — o comportamento que você já tinha
      - Ingredientes Ativos: len(INGREDIENTES_VALIDOS)
      - Benefícios: len(BENEFIT_CANONICAL_ORDER)
      - Categorias: len(CATEGORY_CANONICAL_ORDER)
      - Tipos de pele: contagem única a partir de df['tipo_pele'] (normalizado quando possível)
    """
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    total_produtos = int(df.shape[0])
    total_csvs = int(df["_source_file"].nunique()) if "_source_file" in df.columns else 1
    total_ingredientes = len(INGREDIENTES_VALIDOS)
    total_beneficios = len(BENEFIT_CANONICAL_ORDER)
    total_categorias = len(CATEGORY_CANONICAL_ORDER)
    total_tipos_pele = _count_unique_skin_types(df)

    with c1:
        st.markdown(
            f"""
            <div class="kpi" style="width:250px; padding:15px;">
               <div class="kpi-value">{total_produtos:,}</div>
               <div class="kpi-label" style="font-size:25px;">Produtos</div>
            </div>
            """.replace(",", "."),
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="kpi" style="width:250px; padding:15px;">
               <div class="kpi-value">{total_csvs:,}</div>
               <div class="kpi-label" style="font-size:25px;">Marcas</div>
            </div>
            """.replace(",", "."),
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="kpi" style="width:250px; padding:15px;">
               <div class="kpi-value">{total_categorias:,}</div>
               <div class="kpi-label" style="font-size:25px;">Categorias</div>
            </div>
            """.replace(",", "."),
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="kpi" style="width:250px; padding:15px;">
               <div class="kpi-value">{total_beneficios:,}</div>
               <div class="kpi-label" style="font-size:25px;">Benefícios</div>
            </div>
            """.replace(",", "."),
            unsafe_allow_html=True,
        )

    with c5:
        st.markdown(
            f"""
            <div class="kpi" style="width:250px; padding:15px;">
               <div class="kpi-value">{total_ingredientes:,}</div>
               <div class="kpi-label" style="font-size:25px;">Ingredientes Ativos</div>
            </div>
            """.replace(",", "."),
            unsafe_allow_html=True,
        )

    with c6:
        st.markdown(
            f"""
            <div class="kpi" style="width:250px; padding:15px;">
               <div class="kpi-value">{total_tipos_pele:,}</div>
               <div class="kpi-label" style="font-size:25px;">Tipos de pele</div>
            </div>
            """.replace(",", "."),
            unsafe_allow_html=True,
        )

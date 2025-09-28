from __future__ import annotations
import re
from typing import Tuple, Set, List
from pathlib import Path
import pandas as pd
import streamlit as st

CSV_DIR = Path("/home/usuario/Área de trabalho/Dados/Arquivo")

EXPECTED_COLS = [
    "marca","nome","subtitulo","categoria","quantidade","preco",
    "beneficios","ingredientes","tipo_pele","imagem"
]

def _read_one_csv(p: Path) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(p)
    except Exception as e:
        st.warning(f"Falha ao ler {p.name}: {e}")
        return None

    miss = [c for c in EXPECTED_COLS if c not in df.columns]
    if miss:
        st.warning(f"Pulando {p.name}: colunas ausentes {miss}")
        return None

    df["_source_file"] = p.name  # útil para rastrear a origem
    return df

@st.cache_data(show_spinner=True)
def load_data(path_or_dir: str | Path = CSV_DIR) -> pd.DataFrame:
    """Aceita um caminho de arquivo único OU um diretório com vários CSVs."""
    p = Path(path_or_dir)

    # Coleta arquivos
    if p.is_dir():
        csv_files: List[Path] = sorted(p.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"Nenhum CSV encontrado em: {p}")
        frames = []
        for f in csv_files:
            df = _read_one_csv(f)
            if df is not None:
                frames.append(df)
        if not frames:
            raise ValueError("Nenhum CSV válido com as colunas esperadas foi encontrado.")
        df = pd.concat(frames, ignore_index=True)
    elif p.is_file():
        df = _read_one_csv(p)
        if df is None:
            raise ValueError(f"O CSV {p} não possui as colunas esperadas.")
    else:
        raise FileNotFoundError(f"Caminho inválido: {p}")

    # =================== Normalizações ===================
    # preço -> float (suporta "99,90")
    df["preco"] = (
        df["preco"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.extract(r"([\d\.]*\d(?:\.\d+)?)", expand=False)  # pega número seguro
        .fillna("0")
        .astype(float)
    )

    # quantidade -> separa valor/unidade
    def _split_qty(q: str) -> Tuple[float | None, str | None]:
        if pd.isna(q):
            return None, None
        s = str(q).strip().lower().replace(" ", "")
        m = re.search(r"(\d+(?:[.,]\d+)?)(?:-\d+(?:[.,]\d+)?)?([a-zµ]+)?", s)
        if not m:
            return None, None
        val = float(m.group(1).replace(",", "."))
        unit = m.group(2) if m.group(2) else ""
        return val, unit

    qty = df["quantidade"].apply(_split_qty)
    df["quantidade_valor"]   = qty.apply(lambda t: t[0])
    df["quantidade_unidade"] = qty.apply(lambda t: t[1])

    # strings seguras
    for c in ["beneficios","ingredientes","categoria","marca","tipo_pele","subtitulo","imagem","nome"]:
        if c in df.columns:
            df[c] = df[c].fillna("").astype(str)

    return df

def unique_count_from_semicolon(series: pd.Series) -> int:
    items: Set[str] = set()
    for s in series.dropna().astype(str):
        parts = [p.strip() for p in s.split(";") if p.strip()]
        items.update(parts)
    return len(items)

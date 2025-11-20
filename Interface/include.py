from __future__ import annotations
import sys
import pathlib
import pandas as pd
import streamlit as st          # <- pode ter streamlit aqui, sem problemas
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import re
from typing import Optional, List, Tuple

ROOT = pathlib.Path(__file__).resolve().parent
MODELS_DIR = ROOT / "models"

for path in [ROOT, MODELS_DIR]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

try:
    from core.theme import apply_base_theme, apply_palette_css, PALETTE_OPTIONS, color_sequence
except Exception as e:
    print(f"[AVISO] Erro ao importar core.theme: {e}")

try:
    from core.data import load_data
except Exception as e:
    print(f"[AVISO] Erro ao importar core.data: {e}")

def safe_import(module_name: str, attr_name: str, default):
    try:
        module = __import__(module_name, fromlist=[''])
        return getattr(module, attr_name)
    except Exception:
        print(f"[AVISO] Falha ao importar {attr_name} de {module_name}. Usando padrão.")
        return default

INGREDIENTES_VALIDOS = safe_import("ingredient", "INGREDIENTES_VALIDOS", [])
BENEFIT_CANONICAL_ORDER = safe_import("benefits", "BENEFIT_CANONICAL_ORDER", [])
CATEGORY_CANONICAL_ORDER = safe_import("category", "CATEGORY_CANONICAL_ORDER", [])
SKIN_TYPE_SYNONYMS_PT = safe_import("skin", "SKIN_TYPE_SYNONYMS_PT", {})
SKIN_TYPE_CANONICAL_ORDER = safe_import("skin", "SKIN_TYPE_CANONICAL_ORDER", [])

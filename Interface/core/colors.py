from __future__ import annotations

PALETTE_OPTIONS = [
    "Nebulosa",
    "Solaris",
    "Mar Verde",
    "Oceano",
    "Rubi",
    "Noite Estelar",
    "Rosé & Terra",
    "Fogo Solar",
    "Blush Suave",
        "Brisa Pastel",
    "Citrus & Verde",
    "Primavera",

]

PALETTES = {

  "Nebulosa": {
    "title_grad_from": "#5B21B6",  # roxo profundo
    "title_grad_to":   "#C026D3",  # magenta/rosa forte
    "card_from": "#7F00B2",        # roxo vívido escuro
    "card_to":   "#E57D90",        # rosa queimado elegante (do ref)
    "accent":    "#AB3ED8",        # roxo vibrante
    "seq": [
        "#5B21B6",  # roxo fechado
        "#7F00B2",  # roxo escuro vívido
        "#AB3ED8",  # roxo mais vibrante
        "#C026D3",  # rosa puxado pro magenta
        "#E57D90",  # rosa queimado
        "#F1889B"   # rosa médio suave
    ],
},


    # Cores ok; título com laranja -> goiaba
    "Solaris": {
        "title_grad_from": "#FCA311",  # laranja
        "title_grad_to":   "#FF6B6B",  # goiaba
        "card_from": "#F59E0B",
        "card_to":   "#FF6B6B",
        "accent":    "#FF9F1C",
        "seq": ["#FFD166","#FCA311","#FF9F1C","#FF6B6B","#F7B267","#F4845F"],
    },

    # Verde escuro como principal + rename
    "Mar Verde": {
        "title_grad_from": "#166534",  # verde escuro
        "title_grad_to":   "#16A34A",  # verde médio
        "card_from": "#0F766E",        # verde água profundo
        "card_to":   "#22C55E",        # verde vivo
        "accent":    "#86EFAC",        # verde claro de apoio
        "seq": ["#166534","#16A34A","#0F766E","#22C55E","#34D399","#A7F3D0"],
    },

    # Azuis lindos; troquei um tom que puxava pro roxo por azul claro
    "Oceano": {
        "title_grad_from": "#1E3A8A",
        "title_grad_to":   "#3B82F6",
        "card_from": "#1E40AF",
        "card_to":   "#60A5FA",
        "accent":    "#93C5FD",
        "seq": ["#1E3A8A","#1D4ED8","#3B82F6","#60A5FA","#93C5FD","#38BDF8"],
    },

    # Mantida
    "Rubi": {
        "title_grad_from": "#8B0000",
        "title_grad_to":   "#FF6347",
        "card_from": "#B22222",
        "card_to":   "#FF7F7F",
        "accent":    "#F5F5F5",
        "seq": ["#8B0000","#B22222","#FF6347","#FF7F7F","#F5F5F5","#5C4033"],
    },

    # Nova combinação: apenas roxo + azul (sem verde) + novo nome
    "Noite Estelar": {
        "title_grad_from": "#7F00B2",  # roxo (ref)
        "title_grad_to":   "#0069C0",  # azul (ref)
        "card_from": "#1E3A8A",        # azul marinho
        "card_to":   "#AB3ED8",        # roxo (ref)
        "accent":    "#2196F3",        # azul (ref)
        "seq": ["#7F00B2","#AB3ED8","#0069C0","#2196F3","#97E9FF","#3B82F6"],
    },

    # Marrom título mais escuro + rosa revisado (dusty rose)
    "Rosé & Terra": {
        "title_grad_from": "#5C4033",  # marrom bem escuro
        "title_grad_to":   "#8B5E3C",  # marrom quente
        "card_from": "#D0859E",        # rosa queimado/dusty
        "card_to":   "#E9AFC1",        # rosé suave
        "accent":    "#C7A17A",        # bege/taupe
        "seq": ["#5C4033","#8B5E3C","#D0859E","#E9AFC1","#D2B48C","#F5E6DA"],
    },

    # Tons mais claros para vermelho/laranja/amarelo
    "Fogo Solar": {
        "title_grad_from": "#FFB74D",  # laranja claro
        "title_grad_to":   "#FF8A80",  # vermelho claro
        "card_from": "#FFA726",        # laranja médio claro
        "card_to":   "#FFE082",        # amarelo claro
        "accent":    "#FFD54F",        # dourado claro
        "seq": ["#FF8A80","#FFA726","#FFB74D","#FFE082","#FFD54F","#FFE0B2"],
    },
    "Rosé & Terra": {
    # marrom mais escuro no título
    "title_grad_from": "#4A2F23",  # marrom bem escuro
    "title_grad_to":   "#7A4A34",  # marrom quente médio
    # cartões com rosas mais elegantes (dusty/blush)
    "card_from": "#E57D90",        # rosa queimado elegante
    "card_to":   "#F9AABB",        # rosé médio (entre #f1889b e #f99aaa)
    "accent":    "#C7A17A",        # bege/taupe de apoio
    # sequência baseada no seu ref (suave → claro)
    "seq": ["#E57D90","#F1889B","#F99AAA","#FDB4BF","#FCDDD4","#D48AA0"],
},

# (Opcional) Adicione uma paleta só de rosa inspirada 100% no seu ref:
"Blush Suave": {
    "title_grad_from": "#E57D90",
    "title_grad_to":   "#F1889B",
    "card_from": "#F99AAA",
    "card_to":   "#FCDDD4",
    "accent":    "#FDB4BF",
    "seq": ["#E57D90","#F1889B","#F99AAA","#FDB4BF","#FCDDD4","#F7E6EB"],
},
    # 1ª imagem (azul + pêssego + coral) → cores suaves, vibe alegre
    "Brisa Pastel": {
        "title_grad_from": "#95B8F6",
        "title_grad_to":   "#FA5F49",
        "card_from": "#ADD5FA",
        "card_to":   "#F9A59A",
        "accent":    "#F9D99A",
        "seq": ["#95B8F6","#ADD5FA","#F9D99A","#F9A59A","#FA5F49"],
    },

    # 2ª imagem (laranja + amarelo + verdes) → cítrico/fresco
    "Citrus & Verde": {
        "title_grad_from": "#FB7E00",  # laranja forte
        "title_grad_to":   "#9FC089",  # verde médio
        "card_from": "#FFCC3F",        # amarelo vibrante
        "card_to":   "#79B4B0",        # verde azulado
        "accent":    "#D1DFD2",        # verde pálido
        "seq": ["#FB7E00","#FFCC3F","#D1DFD2","#9FC089","#79B4B0"],
    },

    # 3ª imagem (rosa + verde) → delicado e alegre
    "Primavera": {
        "title_grad_from": "#FE5668",  # rosa forte
        "title_grad_to":   "#64A002",  # verde vivo
        "card_from": "#FF8D8F",
        "card_to":   "#B9D394",
        "accent":    "#FEC1A5",
        "seq": ["#FE5668","#FF8D8F","#FEC1A5","#B9D394","#64A002"],
    },
}

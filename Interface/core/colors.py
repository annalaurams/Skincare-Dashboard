from __future__ import annotations

PALETTE_OPTIONS = [
    "Algodão-Doce",
    "Lavanda",
    "Outono",
    "Solaris",
]

PALETTES = {
    "Solaris": {
        "title_grad_from": "#FFB400",
        "title_grad_to":   "#FF4375",
        "card_from": "#FF9800",
        "card_to":   "#FF6B6B",
        "accent":    "#FF7E01",
        "seq": [
            "#FFB400", "#FFA800", "#FF9800", "#FF8A00", "#FF7E01", "#F97316",
            "#EA580C", "#E28000", "#D46300", "#C2410C", "#B93815", "#FF6B3D",
            "#FF6B6B", "#F2645A", "#E85C50", "#E55A3C", "#FF4375", "#FF5A8E",
            "#FF78A7", "#FF9ABA", "#FFAFC7", "#FFBFD0", "#FFDBC5", "#FF97D9",
        ],
    },

    "Outono": {
        "title_grad_from": "#8C4D2E",
        "title_grad_to":   "#298F8F",
        "card_from": "#C08332",
        "card_to":   "#E26B5A",
        "accent":    "#686230",
        "seq": [
            "#8C4D2E", "#A2573A", "#C08332", "#D08C2A", "#DFAC8D", "#E4DDBF",
            "#A2A183", "#686230", "#91493B", "#D87F4F", "#E26B5A", "#CF4747",
            "#B53866", "#895570", "#C76E7A", "#66B0A5", "#64BEB5", "#298F8F",
            "#008392", "#6A87A5", "#A5C6C4", "#A6C4BC", "#EAE5D9", "#FCF3D3",
        ],
    },

    "Algodão-Doce": {
        "title_grad_from": "#F99FB0",
        "title_grad_to":   "#64BEB5",
        "card_from": "#FFD9D9",
        "card_to":   "#A2AD91",
        "accent":    "#D30C7B",
        "seq": [
            "#D30C7B", "#E35F8D", "#F68FA2", "#F8A8B6", "#FBC2C6", "#FFD9D9",
            "#F7C7A1", "#F4B68E", "#F2A477", "#E58D6D", "#A2AD91", "#B8C3A3",
            "#C9D6B5", "#ACDEAA", "#8FBBAF", "#64BEB5", "#4FA7A5", "#3A8F8F",
            "#BDE7F4", "#9FD6EE", "#8FB7E5", "#C6A6D9", "#B68BCF", "#9F7BBF",
        ],
    },

    "Lavanda": {
        "title_grad_from": "#540089", 
        "title_grad_to":   "#1E6173", 
        "card_from": "#3A0078",
        "card_to":   "#8AAE92",
        "accent":    "#8348A7",        
        "seq": [
            "#1E6173", "#2E7294", "#3484AD", "#34BFB6",
            "#243363", "#32267D", "#3C3295", "#555FA3",
            "#45008B", "#3A0078", "#2F0067", "#540089",
            "#631C99", "#7555A3", "#8348A7", "#987AB4",
            "#B2A4C9", "#CFC5DD", "#8AAE92", "#9FB79E",
            "#A2AD91", "#7A8F6A", "#94A48A", "#C8D6CF",
        ],
    },
}

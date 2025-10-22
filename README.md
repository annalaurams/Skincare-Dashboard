# 🧴 Análise de Dados sobre Produtos de Cuidados Faciais: Um Estudo sobre as Tendências do Mercado Brasileiro

## 📑 Sumário

- [🌟 Visão Geral](#-visão-geral)
- [📂 Estrutura do Projeto](#-estrutura-do-projeto)
- [📊 Formatos de Dados](#-formatos-de-dados)
  - [Exemplo CSV](#exemplo-csv)
  - [Exemplo JSON](#exemplo-json)
  - [Descrição dos Campos](#descrição-dos-campos)
- [⚙️ Configuração e Execução](#%EF%B8%8F-configuração-e-execução)
  - [1. Preparar o Ambiente](#1-preparar-o-ambiente)
  - [2. Gerar os Dados](#2-gerar-os-dados)
  - [3. Rodar o Dashboard](#3-rodar-o-dashboard)
- [📬 Contato](#-contato)

## 🌟 Visão Geral

O projeto visa construir um pipeline utilizando técnicas de **Web Scraping** completo para:

- **Extrair** dados de produtos de skincare de marcas brasileiras (Oceane, Sallve, Creamy, BeYoung, Ollie)
- **Normalizar** informações (categorias, benefícios, ingredientes, tipos de pele) usando módulos próprios
- **Visualizar** dashboard filtros e rankings

---

## 📂 Estrutura do Projeto
```
DADOS/
├── Arquivo/                        # CSVs marcas
├── marcas/                         # Dados das marcas
│   ├── Beyoung/
│   │   ├── images/                 # Imagens baixadas
│   │   ├── Beyoung_products.csv    # CSV padronizado
│   │   ├── Beyoung_products.json   # JSON original (opcional)
│   │   └── main.ipynb              # Web scraping
│   ├── Creamy/
│   │   └── ... (mesma estrutura)
│   ├── Oceane/
│   │   └── ... (mesma estrutura)
│   ├── Ollie/
│   │   └── ... (mesma estrutura)
│   └── Sallve/
│       └── ... (mesma estrutura)
├── Interface/                      # Streamlit
│   ├── .streamlit/                 # Configurações do Streamlit
│   │   └── config.toml             # Tema e configurações
│   ├── core/                       
│   │   ├── data.py                 # Carregamento e validação
│   │   └── utils.py                # Funções auxiliares
│   ├── pages/                      # Páginas do dashboard
│   │   ├── 1_Catálogo.py
│   │   ├── 2_Ingredientes.py
│   │   ├── 3_Benefícios.py
│   │   └── 4_Tipos_de_Pele.py
│   ├── ui_components/              # Componentes reutilizáveis
│   │   ├── filters.py              
│   │   └── cards.py                
│   ├── Principal.py                # Página inicial
│   └── requirements.txt            # Dependências
├── models/                         # Regras de normalização de acordo com produtos
│   ├── benefits.py                 
│   ├── category.py                 
│   ├── ingredient.py               
│   └── skin.py                     
├── models_sem_filtro/              # Regras de normalização geral
└── README.md                       
```

---

## 📊 Formatos de Dados

Os dados são extraídos dos sites das marcas através de web scraping e alguns campos são preenchidos manualmente para garantir a padronização e qualidade das informações.

#### Exemplo CSV:
```csv
marca,nome,subtitulo,categoria,quantidade,preco,beneficios,ingredientes,tipo_pele,imagem
creamy,Creme Retexturizador - Ácido Glicólico,Reduz poros e melhora a textura da pele,creme,30ml,84.20,"antissinais;colágeno;controle da oleosidade;hidratação;minimiza poros;suaviza textura","ácido glicólico;lha;niacinamida;benzoato de sódio;álcool cetílico;hidróxido de amônio;bisabolol",todos os tipos,creme-retexturizador-acido-glicolico.jpg
```

#### Exemplo JSON

```json
{
  "marca": "creamy",
  "nome": "Creme Retexturizador - Ácido Glicólico",
  "subtitulo": "Reduz poros e melhora a textura da pele",
  "categoria": "creme",
  "quantidade": "30ml",
  "preco": 84.20,
  "beneficios": [
    "antissinais",
    "colágeno",
    "controle da oleosidade",
    "hidratação",
    "minimiza poros",
    "suaviza textura"
  ],
  "ingredientes": [
    "ácido glicólico",
    "lha",
    "niacinamida",
    "benzoato de sódio",
    "álcool cetílico",
    "hidróxido de amônio",
    "bisabolol",
    "goma xantana",
    "fenoxietanol",
    "glicerina"
  ],
  "tipo_pele": "todos os tipos",
  "imagem": "creme-retexturizador-acido-glicolico.jpg"
}
```

#### Descrição dos campos:

| Campo | Tipo | Descrição | 
|-------|------|-----------|
| `marca` | string | Nome da marca | 
| `nome` | string | Nome completo do produto | 
| `subtitulo` | string | Descrição curta  | 
| `categoria` | string | Categoria do produto (creme, serum, etc.) | 
| `quantidade` | string | Volume ou peso (ex: "30ml", "50g") | 
| `preco` | float | Preço em R$ (formato: 84.20) | 
| `beneficios` | string | Lista separada por `;` dos benefícios prometidos |
| `ingredientes` | string | Lista separada por `;` dos ingredientes ativos | 
| `tipo_pele` | string | Tipos de pele recomendados, separados por `;` | 
| `imagem` | string | Nome do arquivo de imagem | 

---

## ⚙️ Configuração e Execução

### 1. Preparar o Ambiente
```bash
python -m pip install --upgrade pip

# Instalar dependências principais
pip install requests beautifulsoup4 pandas numpy streamlit altair plotly pillow

pip install selenium webdriver-manager undetected-chromedriver

pip install jupyter
```

### 2. Gerar os Dados

Para cada marca, execute o notebook de scraping:
```bash
jupyter notebook

# Navegue até a pasta da marca e execute main.ipynb
# Exemplo: marcas/Beyoung/main.ipynb
```

O notebook deve:
1. Coletar dados das páginas da marca
2. Aplicar normalização usando `models/`
3. Salvar `<marca>_products.csv` e `<marca>_products.json`

### 3. Rodar o Dashboard
```bash
# Navegar até a pasta Interface
cd Interface

# Executar o Streamlit
streamlit run Principal.py
```
O dashboard abrirá automaticamente em `http://localhost:8501`

---

## 📬 Contato

**Anna Laura Moura**

Estudante de Ciência da Dados | CEFET-MG

[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:nalauramoura@gmail.com)

[![LinkedIn](https://img.shields.io/badge/-LinkedIn-%230077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/annalaurams)



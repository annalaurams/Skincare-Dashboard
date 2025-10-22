# 🧴 Análise de Dados sobre Produtos de Cuidados Faciais: Um Estudo sobre as Tendências do Mercado Brasileiro


## 📑 Sumário

1. [Visão Geral](#-visão-geral)
2. [Estrutura do Projeto](#-estrutura-do-projeto)
3. [Conteúdo das Pastas](#-conteúdo-das-pastas)
   - [Pasta de Marca (Template)](#pasta-de-marca-template)
   - [Interface (Dashboard)](#interface-dashboard)
   - [Models (Normalização)](#models-normalização)
4. [Formatos de Dados](#-formatos-de-dados)
   - [CSV Padronizado](#csv-padronizado)
   - [JSON Schema](#json-schema)
5. [Configuração e Execução](#%EF%B8%8F-configuração-e-execução)
   - [1. Preparar o Ambiente](#1-preparar-o-ambiente)
   - [2. Gerar os Dados](#2-gerar-os-dados)
   - [3. Rodar o Dashboard](#3-rodar-o-dashboard)
6. [Páginas do Dashboard](#-páginas-do-dashboard)
7. [Dependências](#-dependências)
8. [Checklist de Implementação](#-checklist-de-implementação)

---

## 🌟 Visão Geral

O projeto visa construir um pipeline completo para:

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
│   ├── Principal.py                # Página inicial (entry point)
│   └── requirements.txt            # Dependências do dashboard
├── models/                         # Regras de normalização
│   ├── benefits.py                 
│   ├── category.py                 
│   ├── ingredient.py               
│   └── skin.py                     
├── models_sem_filtro/              
└── README.md                       # Este arquivo
```

---

## 📋 Conteúdo das Pastas

### Pasta de Marca (Template)

Cada pasta de marca (`Beyoung/`, `Creamy/`, `Oceane/`, `Ollie/`, `Sallve/`) deve conter:

| Arquivo/Pasta | Descrição |
|---------------|-----------|
| `images/` | Imagens dos produtos (nomeadas por `product_id` ou slug) |
| `<marca>_products.csv` | **Obrigatório** - CSV com dados padronizados |
| `<marca>_products.json` | **Opcional** - JSON bruto ou exportação alternativa |
| `main.ipynb` | Notebook Jupyter com o scraper e pipeline de limpeza |

### Interface (Dashboard)

| Arquivo/Pasta | Descrição |
|---------------|-----------|
| `.streamlit/config.toml` | Configuração de tema e aparência |
| `core/data.py` | Carregamento de dados, validação de schema |
| `core/utils.py` | Funções auxiliares (normalização, parsing) |
| `pages/*.py` | Páginas do dashboard (4 páginas) |
| `ui_components/` | Componentes reutilizáveis (filtros, cards) |
| `Principal.py` | **Entry point** - Página inicial do Streamlit |
| `requirements.txt` | Dependências do dashboard |

### Models (Normalização)

| Módulo | Função |
|--------|--------|
| `benefits.py` | Mapeia e normaliza benefícios dos produtos |
| `category.py` | Classifica produtos em categorias padronizadas |
| `ingredient.py` | Normaliza nomes de ingredientes |
| `skin.py` | Padroniza tipos de pele (oleosa, seca, mista, sensível) |

---

## 📊 Formatos de Dados

### CSV Padronizado

**Colunas obrigatórias** (`EXPECTED_COLS`):
```
product_id,brand,name,category,price,quantity,benefits,ingredients,skin_types,image_filename,scraped_at
```

#### Exemplo de linha:
```csv
BYG001,Beyoung,Sérum Vitamina C,Serum,49.90,30ml,"hidratação;luminosidade;anti-idade","vitamina c;ácido hialurônico;niacinamida","todos os tipos;oleosa",BYG001.jpg,2025-10-22T10:30:00
```

#### Descrição dos campos:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `product_id` | string | ID único do produto |
| `brand` | string | Nome da marca |
| `name` | string | Nome do produto |
| `category` | string | Categoria (Serum, Hidratante, Cleanser, etc.) |
| `price` | float | Preço em R$ |
| `quantity` | string | Quantidade/volume (ex: "30ml", "50g") |
| `benefits` | string | Lista separada por `;` ou `\|` |
| `ingredients` | string | Lista separada por `;` ou `\|` |
| `skin_types` | string | Lista separada por `;` ou `\|` |
| `image_filename` | string | Nome do arquivo de imagem |
| `scraped_at` | string | Timestamp ISO8601 da coleta |

### JSON Schema
```json
{
  "product_id": "BYG001",
  "brand": "Beyoung",
  "name": "Sérum Vitamina C",
  "category": "Serum",
  "price": 49.90,
  "quantity": "30ml",
  "benefits": ["hidratação", "luminosidade", "anti-idade"],
  "ingredients": ["vitamina c", "ácido hialurônico", "niacinamida"],
  "skin_types": ["todos os tipos", "oleosa"],
  "image_filename": "BYG001.jpg",
  "scraped_at": "2025-10-22T10:30:00"
}
```

---

## ⚙️ Configuração e Execução

### 1. Preparar o Ambiente
```bash
# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências principais
pip install requests beautifulsoup4 pandas numpy streamlit altair plotly pillow

# Opcional: para scrapers com Selenium
pip install selenium webdriver-manager undetected-chromedriver

# Opcional: para notebooks
pip install jupyter
```

### 2. Gerar os Dados

Para cada marca, execute o notebook de scraping:
```bash
# Abrir Jupyter
jupyter notebook

# Navegue até a pasta da marca e execute main.ipynb
# Exemplo: marcas/Beyoung/main.ipynb
```

O notebook deve:
1. Coletar dados das páginas da marca
2. Extrair campos relevantes
3. Aplicar normalização usando `models/`
4. Salvar `<marca>_products.csv` e `<marca>_products.json`

### 3. Rodar o Dashboard
```bash
# Navegar até a pasta Interface
cd Interface

# Executar o Streamlit
streamlit run Principal.py
```

O dashboard abrirá automaticamente em `http://localhost:8501`

---

## 📱 Páginas do Dashboard

O dashboard possui **4 páginas** (além da página inicial):

1. **📦 Catálogo** - Visualização completa dos produtos com filtros
2. **🧪 Ingredientes** - Análise e ranking de ingredientes mais comuns
3. **✨ Benefícios** - Estatísticas sobre benefícios prometidos
4. **👤 Tipos de Pele** - Distribuição de produtos por tipo de pele

---

## 📦 Dependências

### Core (obrigatório)
```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
```

### Visualização
```
altair>=5.0.0
plotly>=5.17.0
```

### Scraping
```
requests>=2.31.0
beautifulsoup4>=4.12.0
selenium>=4.15.0  # opcional
```

### Utilidades
```
pillow>=10.0.0
python-dotenv>=1.0.0
```

---

## ✅ Checklist de Implementação

### Arquivos Críticos

- [ ] `Interface/Principal.py` - Entry point do dashboard
- [ ] `Interface/.streamlit/config.toml` - Configuração de tema
- [ ] `Interface/core/data.py` - Funções de carregamento
- [ ] `Interface/core/utils.py` - Funções auxiliares
- [ ] `Interface/pages/1_📦_Catálogo.py`
- [ ] `Interface/pages/2_🧪_Ingredientes.py`
- [ ] `Interface/pages/3_✨_Benefícios.py`
- [ ] `Interface/pages/4_👤_Tipos_de_Pele.py`
- [ ] `Interface/requirements.txt`

### Estrutura de Dados

- [ ] CSVs padronizados com colunas `EXPECTED_COLS`
- [ ] Função `load_data()` carregando todos os CSVs
- [ ] Função `validar_schema()` verificando integridade
- [ ] Models de normalização funcionando

### Template: `config.toml`
```toml
[theme]
primaryColor = "#e91e63"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#0f1720"

[server]
maxUploadSize = 200
```

---

## 👥 Contribuindo

1. Adicione novas marcas criando pasta em `marcas/<nova_marca>/`
2. Siga o template de estrutura (images, CSV, JSON, notebook)
3. Use os módulos `models/` para normalização consistente
4. Teste o carregamento no dashboard antes de commitar

---

## 📝 Notas

- Mantenha `models_sem_filtro/` apenas se necessário para histórico
- Imagens são opcionais mas melhoram a visualização
- O timestamp `scraped_at` ajuda a rastrear atualizações
- Use `;` como separador padrão para listas em CSV

---

**Desenvolvido para análise de produtos de skincare brasileiros 🇧🇷✨**

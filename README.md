# Análise de Dados sobre Produtos de Cuidados Faciais: Um Estudo sobre as Tendências do Mercado Brasileiro

## 📑 Sumário

1. [🌟 Visão Geral](#-visão-geral)
2. [📂 Estrutura do Projeto](#-estrutura-do-projeto)
3. [📊 Formatos de Dados](#-formatos-de-dados)
   - [Exemplo CSV](#exemplo-csv)
   - [Exemplo JSON](#exemplo-json)
   - [Descrição dos campos](#descrição-dos-campos)
4. [⚙️ Configuração e Execução](#️-configuração-e-execução)
   - [1. Preparar o Ambiente](#1-preparar-o-ambiente)
   - [2. Gerar os Dados](#2-gerar-os-dados)
   - [3. Rodar o Dashboard com Streamlit](#3-rodar-o-dashboard-com-streamlit)
5. [📬 Contato](#-contato)

## 🌟 Visão Geral

O projeto visa construir um pipeline utilizando técnicas de **Web Scraping** completo para:

- **Extrair** dados de produtos de skincare de marcas brasileiras (Oceane, Sallve, Creamy, BeYoung, Ollie)
- **Normalizar** informações (categorias, benefícios, ingredientes, tipos de pele, preço e quantidade) usando módulos próprios
- **Visualizar** dashboard com filtros e rankings

---

## 📂 Estrutura do Projeto
```
DADOS/
├── Arquivo/                        # CSVs de cada marca
├── marcas/                         # Dados das marcas
│   ├── Beyoung/
│   │   ├── Beyoung_products.csv    # CSV padronizado
│   │   ├── Beyoung_products.json   # JSON original 
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
└── README.md                       
```

---

## 📊 Formatos de Dados

Os dados são extraídos dos sites das marcas através de web scraping e alguns campos são preenchidos manualmente para garantir a padronização e preenhimento das informações.

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
| `subtitulo` | string | Descrição curta (se tiver) | 
| `categoria` | string | Categoria do produto (creme, serum, etc.) | 
| `quantidade` | string | Volume ou peso (ex: "30ml", "50g") | 
| `preco` | float | Preço em R$ (formato: 84.20) | 
| `beneficios` | string | Lista separada por `;` dos benefícios|
| `ingredientes` | string | Lista separada por `;` dos ingredientes ativos | 
| `tipo_pele` | string | Tipos de pele recomendados, separados por `;` | 
| `imagem` | string | Nome do arquivo de imagem | 

---

## ⚙️ Configuração e Execução

### 1. Preparar o Ambiente
```bash
python -m pip install --upgrade pip

pip install requests beautifulsoup4 pandas numpy streamlit altair plotly pillow

pip install selenium webdriver-manager undetected-chromedriver

pip install jupyter
```

### 2. Gerar os Dados

Para cada marca, siga os passos abaixo:

#### A. Abrir o notebook
```bash
jupyter notebook
```

#### B. Executar o notebook da marca

- Navegue até a pasta da marca correspondente.

**Exemplo:**
```bash
marcas/Beyoung/main.ipynb
```
- Execute o arquivo `main.ipynb`.

#### C. O notebook deve:

1. Coletar os dados das páginas da marca.
2. Aplicar normalização utilizando os modelos em `models/`.
3. Gerar e salvar os arquivos:
   - `<marca>_products.csv`
   - `<marca>_products.json`
     
### 3. Rodar o Dashboard com Streamlit
```bash
cd Interface
streamlit run Principal.py
```

O dashboard abrirá automaticamente em http://localhost:8501


## 📬 Contato

**Anna Laura Moura**

Estudante de Ciência da Dados | CEFET-MG

[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:nalauramoura@gmail.com)
[![LinkedIn](https://img.shields.io/badge/-LinkedIn-%230077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/annalaurams)



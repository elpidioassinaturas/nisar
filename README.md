# NISAR Data Downloader

Script Python para busca e download automatizado de dados do satélite **NISAR** (NASA-ISRO Synthetic Aperture Radar) via [ASF DAAC](https://asf.alaska.edu).

## O que é o NISAR?

O NISAR é um satélite de observação da Terra criado em parceria entre a NASA e a ISRO. Usa radar de abertura sintética (SAR) em duas bandas (L-band e S-band) para mapear a superfície terrestre com precisão de centímetros, independente de nuvens ou luz solar.

## Pré-requisitos

- Python ≥ 3.10
- Conta gratuita na [NASA Earthdata](https://urs.earthdata.nasa.gov)
- Pacote `asf_search` e `pyyaml`

## Instalação

```bash
pip install asf_search pyyaml
```

## Configuração

Copie o arquivo de exemplo e preencha suas credenciais:

```bash
copy nisar_config.yaml.example nisar_config.yaml
```

Edite `nisar_config.yaml`:
- `earthdata.username` / `earthdata.password` — suas credenciais Earthdata
- `search.aoi_wkt` — área de interesse em formato WKT
- `search.start_date` / `search.end_date` — período de busca
- `search.product_type` — tipo de produto NISAR

> **Atenção:** `nisar_config.yaml` está no `.gitignore`. Suas credenciais nunca serão versionadas.

## Uso

```bash
# Listar produtos disponíveis (sem download)
python download_nisar.py --dry-run

# Baixar até 5 produtos (teste)
python download_nisar.py --limit 5

# Baixar todos os produtos encontrados
python download_nisar.py

# Usar arquivo de config diferente
python download_nisar.py --config meu_config.yaml --dry-run
```

## Produtos NISAR disponíveis

| Código | Nome | Nível |
|--------|------|-------|
| `GCOV` | Geocoded Covariance | L2 |
| `RSLC` | Range-Doppler Single Look Complex | L1 |
| `GSLC` | Geocoded Single Look Complex | L2 |
| `GUNW` | Geocoded Unwrapped Interferogram | L2 |
| `GOFF` | Geocoded Offsets | L2 |

## Estrutura do Projeto

```
nisar/
├── download_nisar.py          # Script principal de download
├── nisar_config.yaml.example  # Exemplo de configuração
├── nisar_config.yaml          # Sua configuração (ignorado pelo git)
├── VERSION                    # Versão atual do projeto
├── .gitignore
├── doc/
│   └── CHANGELOG.md           # Histórico de mudanças
└── downloads/                 # Dados baixados (ignorado pelo git)
```

## Versionamento

- A versão atual está em `VERSION`
- Cada alteração incrementa os últimos 3 dígitos (patch): `X.Y.Z`
- Mudanças são registradas em `doc/CHANGELOG.md`
- Commits seguem o padrão: `vX.Y.Z — Descrição da mudança`

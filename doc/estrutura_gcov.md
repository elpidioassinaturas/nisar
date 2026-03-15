# Estrutura do Arquivo NISAR L2 GCOV (.h5)

**Arquivo de referência:**  
`NISAR_L2_PR_GCOV_010_155_D_093_2005_DHDH_A_20260119T231630_20260119T231704_X05010_N_F_J_001.h5`  
**Tamanho:** ~1,8 GB | **Formato:** HDF5 (CF-1.7) | **Produto:** L2 GCOV — Geocoded Covariance

---

## 📛 Convenção de nomes do arquivo

```
NISAR _ L2 _ PR _ GCOV _ 010 _ 155 _ D _ 093 _ 2005 _ DHDH _ A _ 20260119T231630 _ 20260119T231704 _ X05010 _ N _ F _ J _ 001 .h5
  ①     ②    ③    ④      ⑤    ⑥   ⑦   ⑧    ⑨     ⑩   ⑪        ⑫                   ⑬
```

| Campo | Valor | Significado |
|-------|-------|-------------|
| ① | NISAR | Missão |
| ② | L2 | Nível de processamento (L2 = produto geocodificado) |
| ③ | PR | Modo de produção (PR = Production) |
| ④ | GCOV | Tipo de produto: Geocoded Covariance |
| ⑤ | 010 | Número do ciclo orbital |
| ⑥ | 155 | Número da faixa (track) |
| ⑦ | D | Direção da órbita: **D** = Descending |
| ⑧ | 093 | Número do frame geográfico |
| ⑨ | 2005 | Código do modo de feixe (beam) |
| ⑩ | DHDH | Polarizações transmitidas/recebidas: DH = Dual-H (HH + HV) |
| ⑪ | A | Frequência dominante: A = L-band |
| ⑫ | 20260119T231630 | Início da aquisição (UTC): 19/01/2026 às 23:16:30 |
| ⑬ | 20260119T231704 | Fim da aquisição (UTC): 19/01/2026 às 23:17:04 |

---

## 🗂️ Hierarquia de grupos HDF5

O arquivo segue a estrutura `/science/LSAR/GCOV/` com dois ramos principais:
- **`grids/`** — dados de imagem prontos para uso
- **`metadata/`** — informações de suporte (órbita, calibração, processamento)

```
/
├── [attr] Conventions = CF-1.7
├── [attr] contact = nisar-sds-ops@jpl.nasa.gov
├── [attr] institution = NASA JPL
└── science/
    └── LSAR/
        └── GCOV/
            ├── grids/                  ← 🌍 DADOS DE IMAGEM
            │   ├── frequencyA/         ← L-band (1,25 GHz) — resolução 20 m
            │   └── frequencyB/         ← S-band (3,2 GHz)  — resolução 80 m
            └── metadata/               ← ℹ️ METADADOS
                ├── attitude/
                ├── calibrationInformation/
                ├── ceosAnalysisReadyData/
                ├── orbit/
                └── processingInformation/
```

---

## 🌍 GRIDS — Dados de Imagem

### frequencyA — L-band (1,25 GHz)
**Resolução:** 20 m × 20 m | **Dimensão:** 16.236 × 16.668 pixels | **Área:** ~333 km × 333 km  
**Projeção:** UTM zona 18S / WGS84 (EPSG:32718)  
**Polarizações disponíveis:** HH e HV

| Layer | Dimensão | Tipo | Descrição |
|-------|----------|------|-----------|
| **HHHH** | 16236×16668 | float32 | Covariância HH×HH — **backscatter principal** em polarização H. Mede a reflexão de pulsos H recebidos em H. Uso: detecção de vegetação, solos, estruturas urbanas |
| **HVHV** | 16236×16668 | float32 | Covariância HV×HV — **cross-polarização**. Mede a depolarização do sinal (espalhamento volumétrico). Uso: estimativa de biomassa, florestas |
| **mask** | 16236×16668 | uint8 | Máscara de validade: `1` = pixel válido, `0` = parcialmente focado/inválido, `255` = fora da área imageada |
| **numberOfLooks** | 16236×16668 | float32 | Número de looks (amostras médias) por pixel (média≈9.3, max≈37.5). Indica qualidade estatística da estimativa de covariância |
| **rtcGammaToSigmaFactor** | 16236×16668 | float32 | Fator de conversão RTC gamma0→sigma0. Necessário para comparar com outros produtos SAR |
| **xCoordinates** | 16668 | float64 | Vetor de coordenadas X em metros (projeção UTM) |
| **yCoordinates** | 16236 | float64 | Vetor de coordenadas Y em metros (projeção UTM) |
| **xCoordinateSpacing** | scalar | float64 | Espaçamento em X = **20,0 metros** |
| **yCoordinateSpacing** | scalar | float64 | Espaçamento em Y = **-20,0 metros** (negativo: Y decresce de norte para sul) |
| **projection** | scalar | uint32 | Código EPSG da projeção = **32718** (UTM 18S) |
| **numberOfSubSwaths** | scalar | uint8 | Número de sub-swaths = 1 |
| **listOfPolarizations** | 2 | bytes | `['HH', 'HV']` |
| **listOfCovarianceTerms** | 2 | bytes | `['HHHH', 'HVHV']` |

### frequencyB — S-band (3,2 GHz)
**Resolução:** 80 m × 80 m | **Dimensão:** 4.059 × 4.167 pixels  
**Projeção:** UTM zona 18S / WGS84 (EPSG:32718)

Contém os mesmos layers que frequencyA (HHHH, HVHV, mask, numberOfLooks, rtcGammaToSigmaFactor, xCoordinates, yCoordinates), mas com resolução 4× menor. O `numberOfLooks` médio é ≈37.5 (muito mais looks = imagem S-band tem menor speckle).

---

## ℹ️ METADATA — Metadados

### attitude/ — Atitude do satélite
| Dataset | Dimensão | Descrição |
|---------|----------|-----------|
| `time` | 163 | Vetor de tempo (s desde 2026-01-19T00:00:00) |
| `eulerAngles` | 163×3 | Ângulos de Euler: roll, pitch, yaw (graus) |
| `quaternions` | 163×4 | Quaternions de atitude (q0, q1, q2, q3) |
| `attitudeType` | scalar | Tipo: `"Custom"` |

### orbit/ — Órbita do satélite
| Dataset | Dimensão | Descrição |
|---------|----------|-----------|
| `time` | 49 | Vetor de tempo (s desde 2026-01-19T00:00:00) |
| `position` | 49×3 | Posição XYZ em metros (ref: WGS84 G1762) |
| `velocity` | 49×3 | Velocidade XYZ em m/s |
| `orbitType` | scalar | Tipo: `"MOE"` (Medium precision Orbit Ephemeris) |
| `interpMethod` | scalar | Método de interpolação: `"Hermite"` |

### calibrationInformation/ — Calibração radiométrica

#### Por frequência (A e B), por polarização (HH, HV, VH, VV):
| Dataset | Descrição |
|---------|-----------|
| `scaleFactor` | Fator de escala aplicado à amplitude complexa. FreqA=3.7405, FreqB=4.2196 |
| `scaleFactorSlope` | Variação do fator em função do ângulo de elevação = 0.0 |
| `differentialDelay` | Correção de atraso de range aplicada ao canal = 0.0 m |
| `differentialPhase` | Correção de fase aplicada ao canal = 0.0 rad |
| `rfiLikelihood` | Probabilidade de interferência RFI (0=nenhuma, 1=máxima). HH-A≈0.001 |
| `commonDelay` | Atraso de range comum a todos os canais. FreqA = -60.823 m, FreqB = -37.738 m |
| `faradayRotation` | Rotação de Faraday corrigida = 0.0 rad |

#### crosstalk/ — Diafonia entre polarizações (326×334 pixels, complex64)
| Dataset | Descrição |
|---------|-----------|
| `rxHorizontalCrosspol` | Diafonia no receptor H: razão rxV/rxH |
| `rxVerticalCrosspol` | Diafonia no receptor V: razão rxH/rxV |
| `txHorizontalCrosspol` | Diafonia no transmissor H: razão txV/txH |
| `txVerticalCrosspol` | Diafonia no transmissor V: razão txH/txV |
> Todos os valores de crosstalk são 0.0 — fase de pré-calibração

#### noiseEquivalentBackscatter/ — Ruído do sistema (326×334 pixels, float64)
| Dataset | FreqA média | FreqB média | Descrição |
|---------|-------------|-------------|-----------|
| `HH` | 0.00168 | 0.00233 | NESZ em escala linear (DN²) |
| `HV` | 0.00140 | 0.00198 | NESZ em escala linear (DN²) |

#### elevationAntennaPattern/ — Padrão de antena (326×334, complex64)
Padrão de elevação da antena (two-way) para as polarizações HH e HV, usado na correção radiométrica.

### ceosAnalysisReadyData/ — Conformidade CEOS-ARD

| Dataset | Valor |
|---------|-------|
| `ceosAnalysisReadyDataProductType` | `"Normalised Radar Backscatter (NRB)"` |
| `boundingBox` | `POLYGON ((343440 9159840, 343440 8835120, 676800 8835120, 676800 9159840, ...))` EPSG:32718 |
| `outputBackscatterDecibelConversionFormula` | `10*log10(<GCOV_TERM>)` |

### processingInformation/

#### inputs/ — Entradas do processamento
| Dataset | Valor |
|---------|-------|
| `l1SlcGranules` | `NISAR_L1_PR_RSLC_010_155_D_093_...h5` (produto L1 de origem) |
| `demSource` | DEM Copernicus 30m (COP-DEM_GLO-30) reprojetado para WGS84 |
| `orbitFiles` | MOE de 21/01/2026 |
| `tecFiles` | Arquivo TEC (ionosfera) de 19/01/2026 |

#### algorithms/ — Algoritmos usados
| Dataset | Valor |
|---------|-------|
| `geocoding` | GEO-AP (Area-Based SAR Geocoding). DOI: 10.1109/TGRS.2022.3147472 |
| `radiometricTerrainCorrection` | RTC-AP (Area-Based RTC). DOI: 10.1109/TGRS.2022.3147472 |
| `demInterpolation` | `biquintic` |
| `polarimetricSymmetrization` | `disabled` |
| `softwareVersion` | `0.25.7` |

---

## 🐍 Como abrir em Python

```python
import h5py
import numpy as np

FILE = "NISAR_L2_PR_GCOV_...h5"

with h5py.File(FILE, "r") as f:
    # Lê backscatter HH L-band (20 m/pixel)
    hhhh = f["science/LSAR/GCOV/grids/frequencyA/HHHH"][:]
    
    # Máscara de pixels válidos
    mask = f["science/LSAR/GCOV/grids/frequencyA/mask"][:]
    
    # Coordenadas geográficas (UTM 18S)
    x = f["science/LSAR/GCOV/grids/frequencyA/xCoordinates"][:]
    y = f["science/LSAR/GCOV/grids/frequencyA/yCoordinates"][:]

# Aplica máscara e converte para dB
hhhh_valid = np.where(mask == 1, hhhh, np.nan)
hhhh_db = 10 * np.log10(hhhh_valid)

print(f"Shape: {hhhh_db.shape}")       # (16236, 16668)
print(f"Resolução: 20 m")
print(f"X range: {x[0]:.0f} – {x[-1]:.0f} m (UTM 18S)")
print(f"Y range: {y[-1]:.0f} – {y[0]:.0f} m (UTM 18S)")
```

---

## 📐 Conversões importantes

| Operação | Fórmula |
|----------|---------|
| Linear → dB | `10 * log10(HHHH)` |
| gamma0 → sigma0 | `sigma0 = gamma0 * rtcGammaToSigmaFactor` |
| Pixels válidos | `mask == 1` |
| Coordenadas em graus | Reprojetar EPSG:32718 → EPSG:4326 com `pyproj` |

---

## 🗺️ Área coberta pelo produto

- **Projeção:** UTM zona 18S (EPSG:32718)
- **Bounding box (UTM):** X = 343.440 – 676.800 m | Y = 8.835.120 – 9.159.840 m
- **Extensão aproximada:** ~333 km × ~325 km
- **Região:** Noroeste da América do Sul (Peru/Colômbia — baseado na zona UTM 18S e longitude central -75°)
- **Data de aquisição:** 19/01/2026 às 23:16:30 UTC
- **Duração do passe:** ~34 segundos (23:16:30 → 23:17:04)

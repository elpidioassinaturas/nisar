# Changelog — NISAR Download

Todas as mudanças relevantes do projeto são documentadas aqui.  
Formato: `[versão] AAAA-MM-DD — Descrição`

---

## [0.0.8] 2026-03-15

### Adicionado
- Coluna **Zona UTM** na tabela de resultados: calculada a partir das coordenadas do centro da cena
  (ex.: `18S  (EPSG:32718)`)
- Coluna **Bbox (°)**: retângulo envolvente da cena em graus WGS84, extraído do GeoJSON da resposta ASF
  (W/E longitude e S/N latitude)

---

## [0.0.7] 2026-03-15

### Adicionado
- `doc/bandas_gcov.html` — guia técnico completo das bandas do produto GCOV:
  todas as bandas diagonais (HHHH, HVHV, VVVV, RHRH, RVRV) e off-diagonais
  complexas (HHHV, HHVV, HVVV, RHRV), sistema de coordenadas UTM/WGS84,
  estrutura interna HDF5, exemplo Python e tabela resumo

---

## [0.0.6] 2026-03-15

### Adicionado
- `doc/guia_earthdata.html` — guia passo a passo para usuário leigo criar conta
  NASA Earthdata, autorizar o app ASF e configurar o programa de download

---

## [0.0.5] 2026-03-15

### Adicionado
- Coluna **Preview** na tabela: thumbnails SAR (browse images) de cada produto
- Lightbox ao clicar na miniatura — abre a imagem em tela cheia
- Coluna **Direção** (Ascending/Descending) com ícone visual
- Tamanho real dos arquivos corrigido (extraído do dict `bytes` do ASF)

---

## [0.0.4] 2026-03-14

### Corrigido
- Erro `unsupported operand type(s) for /: 'dict' and 'float'` na rota `/api/search`
- Campo `bytes` do ASF retornava `dict` em vez de número — tratamento defensivo adicionado
- Todos os campos de texto da resposta JSON protegidos com `str()` para evitar erros de tipo
- Adicionado `traceback` nos erros da API para facilitar diagnóstico futuro

---

## [0.0.3] 2026-03-14

### Adicionado
- Interface web Flask (`app.py` + `templates/index.html`)
- Aba **Busca e Download**: tabela de produtos, seleção por checkbox, log em tempo real, barra de progresso
- Aba **Configuração**: formulário completo para credenciais, datas, AOI, produto e pasta de destino
- Aba **Arquivos Baixados**: lista arquivos `.h5` já salvos localmente
- `INICIAR.bat` — duplo clique para abrir a interface no navegador
- `requirements.txt` com dependências do projeto

---

## [0.0.2] 2026-03-14

### Corrigido
- Datas de busca no config: corrigido para o período de dados disponíveis (out/2025 – jan/2026)
- Ordem do polígono WKT da AOI (Brasil): corrigida para sentido anti-horário, eliminando aviso `REVERSE`
- Mesmo ajuste aplicado em `nisar_config.yaml.example`

### Verificado
- Dry-run confirmou **50 produtos GCOV** encontrados no Brasil para o período correto

---

## [0.0.1] 2026-03-14

### Adicionado
- Estrutura inicial do projeto
- `.gitignore` com exclusão de credenciais e dados
- `VERSION` como fonte da versão atual
- `CHANGELOG.md` e pasta `doc/`
- Script de download `download_nisar.py` (versão inicial)
- Arquivo de configuração `nisar_config.yaml.example`
- `README.md` com instruções de uso

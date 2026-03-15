# Changelog — NISAR Download

Todas as mudanças relevantes do projeto são documentadas aqui.  
Formato: `[versão] AAAA-MM-DD — Descrição`

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

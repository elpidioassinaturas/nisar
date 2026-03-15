---
name: versioning
description: >
  Fluxo de controle de versão para projetos com Git + GitHub.
  A cada alteração: descreve mudanças em doc/CHANGELOG.md,
  incrementa os últimos 3 dígitos (patch) do arquivo VERSION,
  e faz commit com mensagem padronizada vX.Y.Z — descrição.
---

# Skill: Versionamento com Git

Use este skill sempre que alterar código. Ele garante que cada mudança
fique documentada no changelog e versionada no git.

## Regras

- Versão no arquivo `VERSION` no formato `MAJOR.MINOR.PATCH`
- Cada alteração incrementa o **PATCH** (último dígito): `0.0.1 → 0.0.2`
- Descrição da mudança sempre em `doc/CHANGELOG.md`
- Commit com mensagem: `vX.Y.Z — Breve descrição da mudança`

---

## Passos

### 1. Ler a versão atual

```powershell
$version = (Get-Content VERSION).Trim()
$version
```

### 2. Incrementar o PATCH

```powershell
$parts = $version.Split(".")
$parts[2] = [int]$parts[2] + 1
$newVersion = $parts -join "."
$newVersion | Set-Content VERSION
Write-Host "Nova versão: $newVersion"
```

### 3. Atualizar doc/CHANGELOG.md

Adicione uma entrada no TOPO do arquivo `doc/CHANGELOG.md` com:
- Versão e data de hoje
- O que foi adicionado / modificado / corrigido / removido

Formato:
```markdown
## [X.Y.Z] AAAA-MM-DD

### Adicionado
- Item novo

### Modificado
- O que foi alterado

### Corrigido
- Bug corrigido

### Removido
- O que foi removido
```

### 4. Fazer stage de todos os arquivos

```powershell
git add -A
```

### 5. Fazer o commit com mensagem padronizada

Substitua `<DESCRIÇÃO>` por uma frase curta em português descrevendo a mudança:

```powershell
git commit -m "v$newVersion — <DESCRIÇÃO>"
```

### 6. Push para o GitHub

```powershell
git push origin main
```

---

## Exemplo completo (PowerShell)

```powershell
# Ler versão atual
$version = (Get-Content VERSION).Trim()

# Incrementar PATCH
$parts = $version.Split(".")
$parts[2] = [int]$parts[2] + 1
$newVersion = $parts -join "."
$newVersion | Set-Content VERSION

# Mostrar nova versão
Write-Host "Versão: $version → $newVersion"

# Lembrete: editar doc/CHANGELOG.md antes de continuar!
Write-Host "Edite doc/CHANGELOG.md com a descrição das mudanças, depois execute:"
Write-Host "  git add -A"
Write-Host "  git commit -m `"v$newVersion — DESCRIÇÃO`""
Write-Host "  git push origin main"
```

---

## Notas

- Se a mudança for grande (nova funcionalidade), pergunte ao usuário se deve incrementar MINOR (`0.1.0`) em vez de PATCH
- Se houver quebra de compatibilidade, incremente MAJOR (`1.0.0`)
- O arquivo `nisar_config.yaml` está no `.gitignore` — credenciais NUNCA são versionadas

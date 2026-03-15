# Plano: Suporte a Shapefile como AOI de Entrada

## Objetivo
Permitir que o usuário forneça um arquivo `.shp` (shapefile) como área de interesse para a busca NISAR, em vez de digitar um WKT manualmente.

## Abordagem Técnica

### Backend (`app.py`)
- Nova rota `POST /api/upload-shapefile` que recebe o arquivo `.shp` (e `.dbf`, `.shx`) via ZIP ou upload múltiplo
- Usa **`geopandas`** para ler o shapefile e extrair as geometrias
- Reprojecta para **WGS84 (EPSG:4326)** automaticamente se necessário
- Gera o envelope convexo (`unary_union.convex_hull`) e converte para WKT
- Retorna o WKT + info (nº feições, CRS original) para o frontend

### Frontend (`templates/index.html`)
- Na aba **Configuração**, novo botão "📂 Carregar shapefile"
- Input `<input type="file" accept=".shp,.zip">` — `.shp` direto ou `.zip` com os 3 arquivos
- Após upload: mostra nome do arquivo, nº de feições e preview do WKT
- Campo "Área de interesse (WKT)" preenchido automaticamente

### Dependências novas
Adicionar ao `requirements.txt`:
```
geopandas>=0.14
```
(`pyproj` e `shapely` já são dependências internas do geopandas)

## Fluxo do Usuário
1. Aba **Configuração** → clica "📂 Carregar shapefile"
2. Seleciona `.shp` ou `.zip` (com `.shx` e `.dbf`)
3. Backend lê, reprojecta para WGS84, retorna WKT
4. Campo "Área de interesse (WKT)" preenchido automaticamente
5. Usuário salva config e faz a busca normalmente

## Verificação
- [ ] Testar com shapefile em UTM (reprojeção automática)
- [ ] Testar com shapefile em WGS84 (sem reprojeção necessária)
- [ ] Testar com polígono complexo (convex_hull simplifica para o ASF)
- [ ] Verificar que o WKT gerado é aceito pelo `asf_search`

## Ordem de implementação
1. Instalar `geopandas` e atualizar `requirements.txt`
2. Criar rota `/api/upload-shapefile` em `app.py`
3. Atualizar o HTML: botão de upload + card de preview
4. Testar e commitar v0.0.8

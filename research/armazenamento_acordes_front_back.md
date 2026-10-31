# Armazenamento e processamento dos acordes vindos do front-end

## Resumo (3-6 frases)
Quando o usuário seleciona acordes na tela "Por acordes" (`/poracordes`), o front-end mantém esses acordes em um array no controlador AngularJS, converte-os em uma string separada por vírgula e envia via query string para `GET /similares?acordes=...`. O back-end recebe esse parâmetro com `request.args.get('acordes')`, faz `split(',')` diretamente (sem normalização) e passa essa lista para `get_similares()`. Nesse caminho, `get_similares()` compara com `musica.acordes` (armazenados em memória como `list(set(cifra))` após o parsing da cifra no carregamento do CSV) usando interseção/diferença de conjuntos, filtra por gênero, exclui a própria música se vier via `id_unico_musica` e ordena por `(len(diferenca), -len(intersecao))`. Não existe armazenamento persistente no back-end para os acordes enviados pelo front-end; eles existem apenas durante a requisição HTTP.

## 1) Front-end: como os acordes são coletados e enviados

### Definição dos acordes disponíveis
Em `static/assets/js/controllers/acordes.js:2-53`, o controlador define listas fixas de acordes por tonalidade, cada elemento sendo um objeto `{ 'acorde': '...', 'cor': '...' }`. Esses objetos são agrupados em `vm.acordes` (arrays por raiz: C,D,E,F,G,A,B).

### Coleta dos acordes selecionados
- `vm.meusAcordes = []` (`static/assets/js/controllers/acordes.js:54`).
- `vm.addAcorde(acorde)` (`static/assets/js/controllers/acordes.js:63-71`): se o objeto `acorde` não estiver em `vm.meusAcordes`, adiciona-o; caso já esteja, remove-o pelo índice. Após qualquer alteração, chama `vm.pesquisarPorAcordes()`.
- `vm.temAcorde(acorde)` (`static/assets/js/controllers/acordes.js:72-74`): verifica se `acorde` está em `vm.meusAcordes`.

**Importante:** `vm.meusAcordes` armazena **os próprios objetos `{acorde, cor}`** definidos no front-end, não apenas strings. É esse array que é usado para montar a requisição.

### Montagem da requisição
Em `vm.pesquisarPorAcordes()` (`static/assets/js/controllers/acordes.js:84-115`):
- Se `vm.meusAcordes.length > 0` (`static/assets/js/controllers/acordes.js:85`):
  - `var apiUrl = "";` (`static/assets/js/controllers/acordes.js:91`) — requisições vão para **mesma origem**.
  - `var searchString = "similares?acordes=".concat(createChordsString(vm.meusAcordes));` (`static/assets/js/controllers/acordes.js:92`)
- `createChordsString(chords)` (`static/assets/js/controllers/acordes.js:76-82`):
```js
var createChordsString = function(chords) {
  var str = "";
  for (var i = 0; i < chords.length; i++) {
    str = str.concat(chords[i].acorde, ',');
  }
  return str.substring(0, str.length-1);
}
```
Ou seja, ele percorre `vm.meusAcordes`, pega **apenas** `chords[i].acorde` (a string do acorde) e concatena com vírgula. Exemplo prático: `[ {acorde:'C'}, {acorde:'G'}, {acorde:'Am'} ]` → `"C,G,Am"`.
- Se `vm.meuGenero` estiver definido, adiciona `&generos=` (`static/assets/js/controllers/acordes.js:93-95`).
- Faz `$http.get(apiUrl.concat(searchString))` (`static/assets/js/controllers/acordes.js:96`).

O resultado volta em `data` e é atribuído a `vm.musics` (`static/assets/js/controllers/acordes.js:97-103`).

## 2) Back-end: recebimento e roteamento em `/similares`

Em `GET /similares` (`main.py:170-201`):
- Lê parâmetros: `acordes_tag = request.args.get('acordes')` (`main.py:173`), `id_musica_tag = request.args.get('id_unico_musica')` (`main.py:174`), `sequencia_tag = request.args.get('sequencia')` (`main.py:175`), `pagina_tag = request.args.get('pagina','1')` (`main.py:176`).
- Tratar filtro por gênero: `generos_tag = request.args.get('generos')`; `generos_key = generos` (todos) ou `generos_tag.split(',')` se existir (`main.py:179-183`).
- **Lógica de roteamento:**
```python
acordes = []
if acordes_tag:
    acordes = acordes_tag.split(',')
elif id_musica_tag:
    musica = musicas[id_musica_tag]
    acordes = musica.acordes
elif sequencia_tag:
    acordes = sequencia_tag.replace(',','')
    similares = []
    if acordes in sequencias:
        id_seq = sequencias[acordes]
        similares = get_pagina(get_similares_por_sequencia(id_seq, generos_key), pagina_tag)
    return json.dumps(similares)

similares = get_similares(acordes, generos_key, id_musica_tag)
return json.dumps(get_pagina(similares, pagina_tag))
```
(`main.py:184-201`)

**Ponto importante:** para o caso "por acordes" (seleção direta via tela `/poracordes`), entra no primeiro `if (acordes_tag)`. O back-end faz **apenas** `acordes_tag.split(',')` (`main.py:186`). **Não há normalização, não há conversão, não há armazenamento persistente** — `acordes` é uma lista de strings exatamente como vieram da query string.

Também existe o caso "por música" (`/pormusica`): o front-end envia `similares?id_unico_musica=...` (`static/assets/js/controllers/musica.js:52-69`). Nesse caso, entra no `elif id_musica_tag` e o back-end obtém `acordes = musica.acordes` da música escolhidade em memória (`main.py:187-190`), seguindo o mesmo caminho para `get_similares()`.

## 3) Como os acordes das músicas são armazenados no back-end (contexto)

No carregamento do CSV (`main.py:49-98`):
- `main.py:49-50`: abre `data/top/dataset_final.csv` e pula cabeçalho.
- `main.py:52-56`: para cada linha limpa aspas/`NA`, remove último caractere, divide por `comma`, converte `POPULARIDADE` removendo pontos (`int(musica[POPULARIDADE].replace('.', ''))`.
- `main.py:58-61`: se `musica[CIFRA] != ''`, `musica[CIFRA] = limpa_cifra(musica[CIFRA].split(';'))` senão `[]`.
- `main.py:63`: `musica[SEQ_FAMOSA] = musica[SEQ_FAMOSA].split(";")`.
- `main.py:69-74`: cria objeto `Musica` (`musica.py:1-25`) com os campos e armazenando in `musicas_dict[musica_obj.id_unico_musica]`.
- `main.py:77-78`: adiciona cada acorde de `musica_obj.acordes` ao conjunto `acordes` global (conjunto de **todos** os acordes existentes).
- `main.py:82-85`: adiciona à lista `genero_musicas[musica_obj.genero]`.
- `main.py:88-89`: cria `musicas` (`OrderedDict` ordenado por popularidade decrescente).
- `main.py:95-96`: ordena listas por gênero por popularidade decrescente.

Em `musica.py:5,16-18`:
```python
self.cifra = cifra
self.acordes = list(set(cifra))
self.seqs_famosas = seqs_famosas
```
`limpa_cifra()` (`main.py:11-23`) faz apenas **extração e filtragem** (remove tablaturas com `|` pegando primeiro token, ou divide por espaços; remove strings vazias) — **não há normalização**. `self.acordes = list(set(cifra))` transforma em um **conjunto de acordes únicos** exatamente na forma como foram extraídos. Esses valores são armazenados em memória (em `musicas_dict`/`musicas`/`musica_obj.acordes`) e também compõem o conjunto global `acordes` (`main.py:77-78`, `main.py:163-164` retorna `json.dumps(list(acordes))`).

## 4) Processamento no back-end no caminho por acordes selecionados

Em `get_similares(acordes, generos_key, id_musica = None)` (`main.py:230-263`):
- `collection = apply_filtro(musicas.values(), generos_key)` (`main.py:233`, `main.py:266-272`): para cada gênero em `generos_key`, se estiver em `generos` adiciona todas as músicas de `genero_musicas[genero]` (por ordem de popularidade dentro de gênero).
- Para cada música na coleção: se `musica.id_unico_musica != id_musica` (`main.py:238`) calcula:
  ```python
  inter = set(acordes).intersection(set(musica.acordes))
  diff = set(musica.acordes) - set(acordes)
  ```
  (`main.py:240-241`)
- Se `len(inter) > 0` (`main.py:245`) monta objeto com `diferenca`, `intersecao`, `acordes`, `popularidade`, `genero`, `url`, etc. (`main.py:246-260`).
- Ordena por `(len(diferenca), -len(intersecao))` (`main.py:262-263`).
- `GET /similares` pagina com `get_pagina` (`main.py:226-228`, `main.py:201`) e retorna `json.dumps(...)`.

**Observação:** os acordes vindos do front-end (`acordes` lista de strings após `split(',')`) são usados **diretamente** nas operações de `set` com `musica.acordes` (também strings exatas). Não existe normalização. Se houver diferença entre `#` e `b`, ou entre maiúsculas/minúsculas, não haverá interseção.

## 5) Fluxo completo (passo a passo)
1. **Front-end**: usuário clica em acordes na tela `/poracordes` → `AcordesController.addAcorde` atualiza `vm.meusAcordes` e chama `vm.pesquisarPorAcordes()` (`static/assets/js/controllers/acordes.js:63-97`).
2. **Front-end**: `createChordsString` extrai `acorde` de cada objeto e junta com vírgula → `searchString = "similares?acordes=C,G,Am"` (`static/assets/js/controllers/acordes.js:76-92`). Requisição `$http.get` para mesma origem.
3. **Back-end**: `GET /similares` recebe `acordes_tag`, faz `acordes_tag.split(',')` → lista de strings (`main.py:173,185-187`). Filtra por gênero se houver (`main.py:179-183`). Chama `get_similares(acordes, generos_key, id_musica_tag)` (`main.py:199-201`).
4. **Back-end**: `get_similares` filtra coleção por gênero (`main.py:233`), para cada música calcula interseção/diferença com `musica.acordes` (armazenados em memória), só inclui com interseção > 0, ordena e retorna com `diferenca`/`intersecao` (`main.py:238-263`).
5. **Back-end**: `get_pagina` aplica paginação com `TAM_PAGINA=100` (`main.py:226-228`, `main.py:35`) e `GET /similares` retorna `json.dumps(similares)` (`main.py:201`).
6. **Front-end**: recebe JSON (via `$http`) e atualiza `vm.musics` (`static/assets/js/controllers/acordes.js:97-103`).

## Referências concretas
- `static/assets/js/controllers/acordes.js:2-125` (definição de acordes, coleta, montagem da requisição)
- `main.py:11-23` (`limpa_cifra`)
- `main.py:49-98` (carregamento do CSV e construção dos globais)
- `main.py:170-201` (roteamento em `/similares`)
- `main.py:226-228,230-263,266-272` (`get_pagina`, `get_similares`, `apply_filtro`)
- `musica.py:1-25` (`Musica`: `acordes = list(set(cifra))`)
- `static/assets/js/controllers/musica.js:52-69` (caso "por música" → envia `id_unico_musica`)

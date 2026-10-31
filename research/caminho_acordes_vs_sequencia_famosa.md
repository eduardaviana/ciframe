# Caminho por acordes vs caminho por sequência famosa

## Resumo
No endpoint `GET /similares` existem dois caminhos distintos:
- **Caminho por acordes / por música**: usa `get_similares()` e calcula interseção/diferença entre conjuntos de acordes, retornando `diferenca` e `intersecao` e ordenando os resultados.
- **Caminho por sequência famosa**: usa `get_similares_por_sequencia()` e filtra por uma tag pré-computada (`seqs_famosas`) vinda do CSV. Não calcula interseção/diferença, não ordena os resultados e retorna um objeto com campos diferentes.

## 1) O que é o "caminho por acordes"

O "caminho por acordes" é quando a requisição **não** vem com `sequencia_tag`. Nesse caso, `GET /similares` (`main.py:170-201`) pode receber:

- `acordes` diretamente: `acordes_tag = request.args.get('acordes')` e, se existir, `acordes = acordes_tag.split(',')` (`main.py:173`, `main.py:185-187`).
- `id_unico_musica`: `id_musica_tag = request.args.get('id_unico_musica')` e, se existir (e não vier `acordes_tag`), busca a música em `musicas[id_musica_tag]` e define `acordes = musica.acordes` (`main.py:174`, `main.py:187-190`). `musica.acordes` é `list(set(cifra))` (acordes únicos da cifra), definido em `musica.py:17`.

Em ambos os casos, o código não entra no `elif sequencia_tag` e segue para:

```python
similares = get_similares(acordes, generos_key, id_musica_tag)
return json.dumps(get_pagina(similares, pagina_tag))
```
(`main.py:199-201`)

### O que `get_similares` faz
`get_similares(acordes, generos_key, id_musica = None)` (`main.py:230-263`):
- Filtra por gênero com `apply_filtro(musicas.values(), generos_key)` (`main.py:233`).
- Para cada música, se `musica.id_unico_musica != id_musica` (`main.py:238`): calcula `inter = set(acordes).intersection(set(musica.acordes))` e `diff = set(musica.acordes) - set(acordes)` (`main.py:240-241`).
- Só inclui músicas com `len(inter) > 0` (`main.py:245`).
- Monta o objeto com campos extras:
```python
similar = {
        'id_unico_musica' : musica.id_unico_musica,
        'id_artista' : musica.id_artista,
        'id_musica' : musica.id_musica,
        'nome_artista' : musica.nome_artista,
        'nome_musica' : musica.nome_musica,
        'popularidade' : musica.popularidade,
        'acordes' : musica.acordes,
        'genero' : musica.genero,
        'url' : musica.url,
        'diferenca' : list(diff),
        'intersecao' : list(inter)
}
```
(`main.py:246-260`)
- Ao final, ordena por `(len(diferenca), -len(intersecao))`:
```python
return sorted(similares, key=lambda x: (len(x['diferenca']), -len(x['intersecao'])))
```
(`main.py:262-263`)

## 2) O que acontece no caminho por sequência famosa
No `GET /similares` (`main.py:170-201`):
1. Lê `sequencia_tag = request.args.get('sequencia')` (`main.py:175`).
2. Se existir e não vier por `acordes_tag`/`id_musica_tag`, faz `acordes = sequencia_tag.replace(',','')` (`main.py:190-191`). 
   - Exemplo: frontend (`static/assets/js/controllers/sequencia.js:55-77`) junta os acordes da sequência com vírgula via `createChordsString` (ex: `Bm,G,D,A`) e envia `?sequencia=Bm,G,D,A`. O backend remove as vírgulas → `BmGDA`.
3. Verifica se essa string concatenada existe em `sequencias` (`main.py:40-45`, `main.py:194`).
4. Se sim, obtém `id_seq = sequencias[acordes]` (`main.py:195`) e chama `get_similares_por_sequencia(id_seq, generos_key)`, paginando com `get_pagina` (`main.py:196`).

### As 6 sequências hardcoded
Em `main.py:40-45`:
```python
sequencias = {'BmGDA' : 0,
        'CGAmF' : 1,
        'EmG' : 2,
        'CA7DmG7' : 3,
        'GmF' : 4,
        'CC7FFm' : 5}
```
As chaves são a concatenação dos nomes dos acordes, sem separadores. Os valores são os IDs numéricos pré-definidos (0-5).

### A tag pré-computada vem do CSV
No carregamento (`main.py:49-64`):
- Pula cabeçalho (`main.py:50`).
- Para cada linha limpa aspas/`NA` e remove último caractere (`main.py:53`), divide por vírgula (`main.py:55`).
- `musica[SEQ_FAMOSA] = musica[SEQ_FAMOSA].split(";")` (`main.py:63`). A coluna `SEQ_FAMOSA` (índice 7, `main.py:33`) já vem com IDs numéricos no CSV (no dataset inspecionado há valores `'NA'`, `'0'`, `'1'`, etc.), separados por `;` caso haja múltiplos.
- Ao criar `Musica` (`main.py:69-74`), esse valor é passado e guardado em `self.seqs_famosas = seqs_famosas` (`musica.py:5,18`).

### `get_similares_por_sequencia`
`get_similares_por_sequencia(id_seq, generos_key)` (`main.py:203-223`):
- Filtra por gênero com `apply_filtro(musicas.values(), generos_key)` (`main.py:205`).
- Para cada música na coleção filtrada: `if str(id_seq) in musica.seqs_famosas:` (`main.py:209`).
- Se sim, monta um dict **sem** `diferenca` nem `intersecao`:
```python
similar = {
    'id_unico_musica' : musica.id_unico_musica,
    'id_artista' : musica.id_artista,
    'id_musica' : musica.id_musica,
    'nome_artista' : musica.nome_artista,
    'nome_musica' : musica.nome_musica,
    'popularidade' : musica.popularidade,
    'acordes' : musica.acordes,
    'genero' : musica.genero,
    'url' : musica.url,
}
```
(`main.py:210-221`)
- Faz `similares.append(similar)` e retorna a lista (`main.py:222`).

## 3) Existe ordenação no caminho por sequência?

**Sim, correto: não há ordenação.**

Em `get_similares_por_sequencia` não existe `sorted()`. Os resultados são adicionados na ordem em que o `for` percorre `collection` (`main.py:208-222`). 

A ordem de `collection` vem de `apply_filtro` (`main.py:266-272`): para cada gênero em `generos_key`, se existir em `generos`, concatena `genero_musicas[genero]` inteiro. Dentro de cada `genero_musicas[genero]`, a lista já foi ordenada por popularidade decrescente na inicialização (`main.py:95-96`), mas **não há reordenação global entre diferentes gêneros nem nenhuma ordenação aplicada após a filtragem por `seqs_famosas`**. 

A ordenação por `(len(diferenca), -len(intersecao))` existe **apenas** em `get_similares` (`main.py:262-263`), não em `get_similares_por_sequencia`.

## Exemplo concreto
1. No CSV, uma música tem `SEQ_FAMOSA` com `"0"` → no carregamento vira `['0']` (`main.py:63`) e fica em `musica.seqs_famosas` (`musica.py:18`).
2. Usuário seleciona a sequência famosa `BmGDA` no frontend (`static/assets/js/controllers/sequencia.js:2-9`). `createChordsString` gera `"Bm,G,D,A"`. Requisição: `GET /similares?sequencia=Bm,G,D,A`.
3. Backend: `sequencia_tag.replace(',','')` → `"BmGDA"`. Está em `sequencias` com valor `0`. Chama `get_similares_por_sequencia(0, generos_key)`.
4. Para essa música, `str(0) in ['0']` é `True` → é adicionada ao resultado. O objeto não tem `diferenca`/`intersecao`. A ordem depende da ordem de `collection` (por gênero conforme `generos_key`, e popularidade apenas dentro de cada lista de gênero), sem reordenação global.

**Ponto-chave:** a comparação é por **tag pré-computada** (`musica.seqs_famosas`), não por cálculo dinâmico da sequência a partir da cifra da música no momento da requisição.

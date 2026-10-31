# Por que interseção/diferença no caminho por acordes?

## Resposta direta
Sim. O "caminho por acordes" é justamente aquele em que você **seleciona acordes** na tela "Por acordes" (`/poracordes`). 

Quando você clica nos hexágonos de acordes, `AcordesController.addAcorde` adiciona/remove em `vm.meusAcordes` e chama `vm.pesquisarPorAcordes()` (`static/assets/js/controllers/acordes.js:63-75`). Em `vm.pesquisarPorAcordes()` (`static/assets/js/controllers/acordes.js:84-115`), se houver acordes selecionados, ele monta:
```js
var searchString = "similares?acordes=".concat(createChordsString(vm.meusAcordes));
```
onde `createChordsString` junta os acordes com vírgula (`static/assets/js/controllers/acordes.js:76-82`). Ou seja, a requisição vai para `GET /similares?acordes=C,G,Am,...` (mesma origem, `apiUrl` vazio em `static/assets/js/controllers/acordes.js:91`).

## Como isso chega no backend
Em `GET /similares` (`main.py:170-201`):
- Lê `acordes_tag = request.args.get('acordes')` (`main.py:173`).
- Se `acordes_tag` existir (e não for o caso de `sequencia_tag`), faz `acordes = acordes_tag.split(',')` (`main.py:185-187`).
- Não entra no `elif sequencia_tag`. Chama `get_similares(acordes, generos_key, id_musica_tag)` e pagina o resultado (`main.py:199-201`).

Também existe o caso "por música" (`/pormusica`): o frontend envia `GET /similares?id_unico_musica=...` (`static/assets/js/controllers/musica.js:52-69`). Nesse caso, o backend busca a música (`main.py:187-190`) e define `acordes = musica.acordes` (os acordes únicos da música, `musica.py:17`), seguindo o **mesmo caminho** em `get_similares`.

## Por que calcular interseção e diferença?
A ideia é: dado um **conjunto de acordes que você já sabe tocar** (ou os acordes de uma música de referência), encontrar **outras músicas** que compartilhem pelo menos alguns desses acordes, mostrando:
- **`intersecao`**: quais acordes em comum existem entre os acordes solicitados e os acordes da música candidata (`main.py:240`, `main.py:257`).
- **`diferenca`**: quais acordes a música candidata tem, mas **não** estão no conjunto solicitado (`main.py:241`, `main.py:256`).

O código faz isso exatamente assim:
```python
inter = set(acordes).intersection(set(musica.acordes))
diff = set(musica.acordes) - set(acordes)
```
(`main.py:240-241`)

Só são incluídas músicas com `len(inter) > 0` (`main.py:245`). 

Os objetos retornados nesse caminho incluem esses campos:
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

## Por que ordenar assim?
Ao final, o resultado é ordenado por:
```python
return sorted(similares, key=lambda x: (len(x['diferenca']), -len(x['intersecao'])))
```
(`main.py:262-263`)

Ou seja, a ordenação prioriza músicas com **menos acordes diferentes** (menor `len(diferenca)`) e, em caso de empate nesse critério, **mais acordes em comum** (maior `len(intersecao)`, por causa do sinal negativo). Não há outro critério explícito nesse `sorted`.

## Diferença em relação ao caminho por sequência famosa
No caminho por sequência famosa (`?sequencia=...`), o backend não usa `get_similares`. Ele mapeia a string concatenada para um ID numérico (`main.py:40-45, 194-196`) e filtra por tag pré-computada com `get_similares_por_sequencia` (`main.py:203-223`), onde a comparação é `if str(id_seq) in musica.seqs_famosas:` (`main.py:209`). Nesse caminho **não** há cálculo de interseção/diferença, **não** há ordenação explícita e os objetos **não** têm `diferenca`/`intersecao` (`main.py:210-221`).

## Observação importante (tal como está)
- `musica.acordes` é `list(set(cifra))` (`musica.py:17`), ou seja, são **acordes únicos** da cifra da música. A interseção/diferença é feita sobre esses conjuntos únicos.
- A filtragem por gênero é feita via `apply_filtro` antes da comparação (`main.py:233`, `main.py:266-272`).
- A mesma música de referência é excluída quando vem via `id_unico_musica` (`main.py:238`).

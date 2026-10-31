# Explicação com exemplo: por que `ng-hide="music.diferenca.length"` não afeta o caminho por sequência

## Resumo
O filtro `ng-hide="music.diferenca.length"` só esconde cards quando existe a propriedade `diferenca` com valor em array e `length > 0`. No caminho por acordes/música, `get_similares()` (`main.py:230-263`) calcula `intersecao` e `diferenca` e os adiciona ao objeto (`main.py:246-260`). No caminho por sequência, `get_similares_por_sequencia()` (`main.py:203-223`) **não** calcula nem adiciona `diferenca`/`intersecao` (`main.py:210-221`), então esses campos não existem. Como `undefined.length` não é > 0, o filtro não esconde nada nesse caminho.

## Exemplo concreto

### Exemplo 1: caminho por acordes/música
Requisição: `GET /similares?acordes=C,G,Am,F` (ou `?id_unico_musica=...`).
- Backend entra em `main.py:185-187` ou `main.py:187-190`, chama `get_similares(acordes, generos_key, id_musica_tag)` (`main.py:199-201`).
- Em `get_similares` (`main.py:240-241`): calcula `inter = set(acordes).intersection(set(musica.acordes))`, `diff = set(musica.acordes) - set(acordes)`. Só inclui se `len(inter)>0` (`main.py:245`).
- Objeto retornado (exemplo):
```json
{
  "id_unico_musica": "legiao-urbana-tempo-perdido",
  "id_artista": "legiao-urbana",
  "id_musica": "tempo-perdido",
  "nome_artista": "Legião Urbana",
  "nome_musica": "Tempo Perdido",
  "popularidade": 12345,
  "acordes": ["Am", "F", "C", "G"],
  "genero": "Rock",
  "url": "http://www.cifraclub.com.br/legiao-urbana/tempo-perdido",
  "diferenca": ["Am"],
  "intersecao": ["F", "C", "G"]
}
```
No template `static/templates/sequencia.html:43`, `ng-hide="music.diferenca.length"` avalia como `ng-hide="1"`, ou seja, **esconde** esse card. Se `diferenca` fosse `[]`, avaliaria como `ng-hide="0"` (falso), **não esconde**.

### Exemplo 2: caminho por sequência famosa
Requisição: `GET /similares?sequencia=C,G,Am,F` (enviado pelo front-end `SequenciaController` em `static/assets/js/controllers/sequencia.js:73`).
- Backend em `main.py:190-197`: `sequencia_tag.replace(',','')` → `CGAmF`, verifica se está em `sequencias` (`main.py:40-45`), obtém `id_seq = 1`, chama `get_similares_por_sequencia(1, generos_key)`, pagina e retorna.
- Em `get_similares_por_sequencia()` (`main.py:203-223`): filtra por gênero, percorre coleção, se `str(id_seq) in musica.seqs_famosas` (`main.py:209`) adiciona objeto **sem** `diferenca` e **sem** `intersecao` (`main.py:210-221`).
- Objeto retornado (exemplo):
```json
{
  "id_unico_musica": "5-seconds-of-summer-broken-pieces",
  "id_artista": "5-seconds-of-summer",
  "id_musica": "broken-pieces",
  "nome_artista": "5 Seconds Of Summer",
  "nome_musica": "Broken Pieces",
  "popularidade": 45678,
  "acordes": ["C", "G", "Am", "F"],
  "genero": "Pop Rock",
  "url": "http://www.cifraclub.com.br/5-seconds-of-summer/broken-pieces",
}
```
Note que **não existem** `diferenca` nem `intersecao`. No template, `ng-hide="music.diferenca.length"` tenta acessar `music.diferenca` que é `undefined`, então `undefined.length` é `undefined`. Em JavaScript, `undefined` é falsy, então `ng-hide="undefined"` resulta em **não esconder** o card. O card é exibido normalmente.

## O que "não possuir diferença/interseção" implica
Significa: **não há cálculo de comparação entre "acordes que você tem" e "acordes da música"**. No caminho por acordes/música, o propósito é mostrar "quais acordes preciso aprender" (`diferenca`) e "quais já conheço" (`intersecao`), e o front-end usa `diferenca` para filtrar. No caminho por sequência, a busca é feita por **tag pré-computada** (`musica.seqs_famosas` vinda do CSV, `main.py:63`, `musica.py:18`) mapeada por ID (`main.py:40-45`), **não por interseção de conjuntos de acordes**. Por isso não existem esses campos e o filtro `ng-hide` não tem efeito — não é um "filtro para remover", é um filtro que **só existe** quando esses campos estão presentes.

## Referências concretas
- `static/templates/sequencia.html:42-43`
- `main.py:203-223` (`get_similares_por_sequencia`)
- `main.py:230-263` (`get_similares`)
- `main.py:190-197` (roteamento por sequência)
- `main.py:199-201` (roteamento por acordes/música)
- `static/assets/js/controllers/sequencia.js:63-90`
- `static/assets/js/controllers/acordes.js:84-115`
- `static/assets/js/controllers/musica.js:52-69`
- `research/caminho_acordes_vs_sequencia_famosa.md`
- `research/mecanismo_sequencias_famosas.md`
- `research/explicacao_ng_hide_diferenca.md` (documentação anterior)
- `research/front_end_porsequencia.md` (mapeamento do front)
- `musica.py:18` (`seqs_famosas`)
- `data/top/dataset_final.csv` (coluna `SEQ_FAMOSA`) 
- `docs/adr/0001-local-only-docker-deploy.md`
- `docs/adr/0003-lift-frontend-freeze.md`
- `README.md`
- `AGENTS.md`
- `CONTRIB.md`
- `LICENSE`
- `requirements.txt`
- `Dockerfile`
- `static/index.html`
- `static/assets/js/app.js`
- `static/assets/js/routes.js`
- `static/assets/js/controllers/main.js`
- `static/assets/js/controllers/home.js`
- `static/assets/js/controllers/about.js`
- `static/assets/js/directives/df-hex.js`
- `static/templates/directives/` 
- `static/templates/home.html`
- `static/templates/acordes.html`
- `static/templates/musica.html`
- `static/templates/about.html` 
- `static/assets/css/*`
- `static/assets/js/ngprogress.js`
- `static/bower.json`
- `static/.bowerrc`
- `static/favicon.ico`
- `scripts/build-chords-transitions.R`
- `docs/features/sequencias-customizadas/01-research.md`
- `docs/adr/0002-frontend-angularjs-legacy.md`
- `research/*` (todos os arquivos no diretório research)
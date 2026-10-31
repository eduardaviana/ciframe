# Explicação: `ng-hide="music.diferenca.length"`

## O que significa
No template `static/templates/sequencia.html:43`:
```html
ng-hide="music.diferenca.length"
```
Isso significa: **esconder o elemento se `music.diferenca` existir e tiver comprimento > 0**. Em AngularJS, `ng-hide` adiciona a classe `ng-hide` quando a expressão é verdadeira.

## Por que isso funciona diferente por caminho?

### Caminho por acordes / por música (`/poracordes` ou `?id_unico_musica=...`)
O backend chama `get_similares()` (`main.py:199-201`). Essa função constrói objetos com os campos extras:
```python
similar = {
    'id_unico_musica' : musica.id_unico_musica,
    ...
    'acordes' : musica.acordes,
    'genero' : musica.genero,
    'url' : musica.url,
    'diferenca' : list(diff),
    'intersecao' : list(inter)
}
```
(`main.py:246-260`)
Ou seja, **todas** as músicas retornadas por esse caminho possuem as propriedades `diferenca` e `intersecao` (arrays). Se `diferenca.length > 0`, o `ng-hide` avalia como verdadeiro e **esconde** o card. 

### Caminho por sequência famosa (`/porsequencia`)
O backend entra no `elif sequencia_tag` (`main.py:190-197`), mapeia a sequência concatenada para um ID numérico via `sequencias` (`main.py:40-45,194-195`), chama `get_similares_por_sequencia(id_seq, generos_key)` e retorna paginado. 

Em `get_similares_por_sequencia()` (`main.py:203-223`), os objetos são montados **sem** `diferenca` nem `intersecao`:
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

Portanto, `music.diferenca` **não existe** para esses objetos. Em JavaScript/AngularJS, acessar uma propriedade inexistente retorna `undefined`. `undefined.length` avalia como `undefined` (falso em um contexto booleano), então `ng-hide="music.diferenca.length"` resulta em `false` e o card **não é escondido**.

## Conclusão
O `ng-hide="music.diferenca.length"` foi provavelmente escrito pensando no caminho por acordes (onde só faz sentido mostrar músicas com interseção e onde `diferenca` indica quantos acordes faltam). No caminho por sequência, como os objetos não têm `diferenca`, a expressão é falsa e **nenhum resultado é removido pelo filtro**. É por isso que eu disse "As músicas do caminho por sequência não possuem diferenca/intersecao; portanto, o filtro ng-hide não remove nenhum resultado nesse caminho." - não é uma regra geral, é uma consequência do formato diferente dos objetos retornados por cada função.

## Referências concretas
- `static/templates/sequencia.html:42-43`
- `main.py:203-223` (`get_similares_por_sequencia` - sem `diferenca`/`intersecao`)
- `main.py:230-263` (`get_similares` - com `diferenca`/`intersecao`)
- `main.py:190-197` (roteamento `/similares` por `sequencia`) 
- `main.py:199-201` (roteamento por `acordes`/`id_unico_musica`) 
- `static/assets/js/controllers/sequencia.js:63-90` (envio da requisição por sequência) 
- `static/assets/js/controllers/acordes.js:84-115` (envio da requisição por acordes) 
- `static/assets/js/controllers/musica.js:52-69` (envio da requisição por música) 
- `research/front_end_porsequencia.md` (contexto da página) 
- `research/caminho_acordes_vs_sequencia_famosa.md` (diferença entre caminhos) 
- `research/mecanismo_sequencias_famosas.md` (mecanismo pré-computado) 
- `research/composicao_cifras_por_sequencia_famosa.md` (composição das cifras) 
- `research/condicoes_sequencias_famosas_dataset.md` (condições no dataset) 
- `research/sequencia_aparece_seguida.md` (aparecimento contíguo) 
- `research/armazenamento_acordes_front_back.md` (fluxo front-back) 
- `research/normalizacao_acordes.md` (normalização) 
- `research/sem_banco_dados_e_docker.md` (sem banco/Docker) 
- `research/codebase_research_20251028_pt.md` (pesquisa geral) 
- `research/codebase_research_20251028.md` (pesquisa geral) 
- `research/docker_unico_e_banco_embarcado_existente.md` (docker único) 
- `research/analise_cifras_por_sequencia_famosa.md` (análise prévia) 
- `research/caminho_acordes_vs_sequencia_famosa.md (outras versões) |
- `docs/adr/0001-local-only-docker-deploy.md`
- `docs/adr/0003-lift-frontend-freeze.md` 
- `README.md`
- `AGENTS.md` 
- `CONTRIB.md`
- `LICENSE`
- `requirements.txt`
- `Dockerfile` 
- `musica.py`
- `static/index.html` 
- `static/assets/js/app.js`
- `static/assets/js/routes.js` 
- `static/assets/js/controllers/main.js`
- `static/assets/js/controllers/home.js` 
- `static/assets/js/controllers/about.js` 
- `static/assets/js/directives/df-hex.js` 
- `static/templates/directives/` (diretiva templates) 
- `static/templates/home.html`
- `static/templates/acordes.html`
- `static/templates/musica.html`
- `static/templates/about.html` 
- `data/top/dataset_final.csv` (referenciado) 
- `static/assets/js/controllers/sequencia.js` 
- `static/assets/js/controllers/acordes.js` 
- `static/assets/js/controllers/musica.js` 
- `static/assets/css/*`, `static/assets/js/ngprogress.js` (referenciados) 
- `static/bower.json`, `static/.bowerrc` 
- `static/favicon.ico` 
- `scripts/build-chords-transitions.R` 
- `docs/features/sequencias-customizadas/01-research.md` 
- `docs/adr/0002-frontend-angularjs-legacy.md` 
- `docs/adr/0001-local-only-docker-deploy.md` (já listado)
- `docs/adr/0003-lift-frontend-freeze.md` (já listado) 
- `docs/adr/0002-frontend-angularjs-legacy.md` 
- `research/*` (todos os arquivos existentes no diretório research)
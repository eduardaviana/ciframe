# Como o front-end monta a página "Por sequência" (/porsequencia)

## Resumo (3-6 frases)
A página `/porsequencia` é montada pelo template `static/templates/sequencia.html` e controlada por `SequenciaController` (`static/assets/js/controllers/sequencia.js`). O controller define **4 sequências famosas hardcoded** com objetos contendo `acorde` e `cor`, as armazena em `vm.sequenciasFamosas` e as exibe no template com a diretiva `df-hex`. Ao clicar em uma sequência, o controller armazena em `vm.minhaSequencia`, monta a query string concatenando os acordes com vírgula e chama `GET /similares?sequencia=...` (opcionalmente com `&generos=...`). O resultado é exibido em cards, ordenado por `-popularidade` no template, mas filtrando para exibir apenas músicas onde `music.diferenca.length` não existe (pois o caminho por sequência não retorna `diferenca`/`intersecao`).

## 1) Roteamento
Em `static/assets/js/routes.js:17-21`:
```js
.when('/porsequencia', {
  templateUrl: "templates/sequencia.html",
  controller: "SequenciaController",
  controllerAs: "Sequencia"
})
```
O controller é acessado como `Sequencia` no template.

## 2) Controller: definição das sequências famosas
`SequenciaController` (`static/assets/js/controllers/sequencia.js:1-45`):
- Cria 4 objetos hardcoded:
```js
var sequencia1 = { 'index': 1, 'acordes': [ { 'acorde': 'Bm', 'cor': '#2E1C74' }, { 'acorde': 'G', 'cor': '#2E1C74' }, { 'acorde': 'D', 'cor': '#2E1C74' }, { 'acorde': 'A', 'cor': '#2E1C74' } ]};
var sequencia2 = { 'index': 1, 'acordes': [ { 'acorde': 'C', 'cor': '#2E1C74' }, { 'acorde': 'G', 'cor': '#2E1C74' }, { 'acorde': 'Am', 'cor': '#2E1C74' }, { 'acorde': 'F', 'cor': '#2E1C74' } ]};
var sequencia3 = { 'index': 1, 'acordes': [ { 'acorde': 'Gm', 'cor': '#2E1C74' }, { 'acorde': 'F', 'cor': '#2E1C74' } ]};
var sequencia4 = { 'index': 1, 'acordes': [ { 'acorde': 'C', 'cor': '#2E1C74' }, { 'acorde': 'C7', 'cor': '#2E1C74' }, { 'acorde': 'F', 'cor': '#2E1C74' }, { 'acorde': 'Fm', 'cor': '#2E1C74' } ]};
```
(`static/assets/js/controllers/sequencia.js:2-31`)
- `vm.sequenciasFamous = []` e faz `push` das 4 (`static/assets/js/controllers/sequencia.js:33-37`).
- Inicializa estados: `vm.minhaSequencia = {}`, `vm.musics = []`, `vm.generos = GENEROS`, `vm.meuGenero = ""`, `vm.esfigeSpeech = ""`, `vm.isSearching = false`, `vm.showSearchResultsCount = false` (`static/assets/js/controllers/sequencia.js:38-45`).

## 3) Template: exibição das sequências e resultados
`static/templates/sequencia.html`:
- Painel esquerdo (`col-sm-6 col-md-4`): 
```html
<h4 class="text-center">Aponte uma sequencia de acordes</h4>
<div class="acordes-container" ng-repeat='sequencia in Sequencia.sequenciasFamosas' ng-click="Sequencia.pesquisarPorSequencia(sequencia)">
  <df-hex acorde="{{acordeon.acorde}}" acorde-color="{{acordeon.cor}}" acorde-checked="Sequencia.temAcorde(acordeon)" ng-repeat="acordeon in sequencia.acordes"></df-hex>
</div>
```
(`static/templates/sequencia.html:5-8`) - Para cada sequência em `Sequencia.sequenciasFamosas`, renderiza os hexágonos com `df-hex`. Clicar chama `Sequencia.pesquisarPorSequencia(sequencia)`.
- Botão "Encontrei essas músicas" aparece se `Sequencia.showSearchResultsCount` (`static/templates/sequencia.html:10-14`).
- Painel direito (`col-sm-6 col-md-8`): mostra header com `Sequencia.esfigeSpeech` e selecionador de gênero quando `Sequencia.minhaSequencia.acordes.length` (`static/templates/sequencia.html:19-38`). O filtro de gênero chama `Sequencia.pesquisarPorSequencia()` no `ng-change` (`static/templates/sequencia.html:28`). Ao clicar nos hexágonos da sequência selecionada, chama `Sequencia.limparPesquisa()` (`static/templates/sequencia.html:34`).
- Lista de resultados: 
```html
<div class="col-sm-6 col-lg-4"
  ng-repeat="music in Sequencia.musics | orderBy:'-popularidade'"
  ng-hide="music.diferenca.length">
  <div class="music-card" ng-click="Sequencia.goToLirics(music)">
    ...
    <p class="music-title">{{music.nome_musica}}</p>
    <p class="music-artist">{{music.nome_artista}}</p>
    <p class="music-gender"><span class="label label-default">{{music.genero}}</span></p>
  </div>
</div>
```
(`static/templates/sequencia.html:40-59`) - Ordena por `-popularidade`. **Importante:** esconde músicas onde `music.diferenca.length` existe. Como o caminho por sequência (`get_similares_por_sequencia` em `main.py:203-223`) **não** retorna `diferenca` nem `intersecao`, essas músicas **não** são escondidas por esse filtro; no caminho por acordes elas têm `diferenca` e seriam filtradas.

## 4) Lógica do controller

### `vm.temAcorde(acorde)` 
`static/assets/js/controllers/sequencia.js:47-53` - Verifica se `acorde` está em `vm.minhaSequencia.acordes`. Usado no template com `acorde-checked="Sequencia.temAcorde(acordeon)"` para marcar visualmente.

### `createChordsString(chords)`
`static/assets/js/controllers/sequencia.js:55-61` - Itera pelos objetos `{acorde, cor}`, concatena `chords[i].acorde` com vírgula, remove última vírgula. Resultado é string como `Bm,G,D,A`.

### `vm.pesquisarPorSequencia(sequencia)`
`static/assets/js/controllers/sequencia.js:63-90`:
- Se `sequencia` for passada, atribui `vm.minhaSequencia = sequencia` (`static/assets/js/controllers/sequencia.js:64-66`).
- Inicia progresso, define mensagens, limpa `vm.musics`, seta `vm.isSearching = true` (`static/assets/js/controllers/sequencia.js:67-70`).
- Monta query: `var searchString = "similares?sequencia=".concat(createChordsString(vm.minhaSequencia.acordes))` (`static/assets/js/controllers/sequencia.js:72-73`). Adiciona `&generos=` se `vm.meuGenero` existir (`static/assets/js/controllers/sequencia.js:74-76`).
- Chama `$http.get(apiUrl.concat(searchString))` onde `apiUrl = ""` (mesma origem) (`static/assets/js/controllers/sequencia.js:77`). No sucesso, finaliza progresso, atualiza mensagens, `vm.musics = data`, `vm.showSearchResultsCount = true` (`static/assets/js/controllers/sequencia.js:78-83`). Em caso de erro, atualiza mensagens (`static/assets/js/controllers/sequencia.js:85-89`).

### Outros métodos
- `vm.limparPesquisa()` (`static/assets/js/controllers/sequencia.js:92-95`): zera `vm.minhaSequencia = {}` e limpa `vm.musics`.
- `vm.goToLirics(music)` (`static/assets/js/controllers/sequencia.js:97-99`): abre `music.url` em nova janela.
- `vm.goToResults()` (`static/assets/js/controllers/sequencia.js:101-104`): rola até `#results`.

## 5) Fluxo completo
1. **Carregamento**: route `/porsequencia` carrega `sequencia.html` com `SequenciaController` (controllerAs `Sequencia`). O controller popula `vm.sequenciasFamosas` com 4 sequências hardcoded.
2. **Exibição**: template exibe cada sequência como blocos de `df-hex` com os acordes. `ng-click` em cada `acordes-container` chama `pesquisarPorSequencia(sequencia)`.
3. **Seleção**: ao clicar, `vm.minhaSequencia` recebe a sequência selecionada, controller monta `similares?sequencia=Bm,G,D,A` (com vírgula) e faz GET para o backend.
4. **Backend**: `main.py:190-197` remove vírgulas (`sequencia_tag.replace(',','')`), verifica se está em `sequencias` (`main.py:40-45`), obtém ID, chama `get_similares_por_sequencia()` (`main.py:203-223`) filtrando por tag pré-computada `seqs_famosas`.
5. **Exibição dos resultados**: backend retorna lista sem `diferenca`/`intersecao`; front-end recebe, atualizes esfigeSpeech, exibe cards ordenados por `-popularidade` (`static/templates/sequencia.html:42`), sem o filtro `ng-hide` que existe para o caminho por acordes.

## Referências concretas
- `static/assets/js/routes.js:17-21`
- `static/assets/js/controllers/sequeria.js:1-105` (note: nome correto é `sequencia.js`)
- `static/assets/js/controllers/sequencia.js:2-105`
- `static/templates/sequencia.html:1-63` 
- `static/assets/js/directives/df-hex.js:1-12`
- `main.py:40-45,170-197,203-223` (backend) 
- `musica.py:18` (`seqs_famosas`) 
- `data/top/dataset_final.csv (SEQ_FAMOSA)`

## Observação
No template, `ng-repeat="music in Sequencia.musics | orderBy:'-popularidade'"` e `ng-hide="music.diferenca.length"` (`static/templates/sequencia.html:42-43`). As músicas do caminho por sequência não possuem `diferenca`/`intersecao`; portanto, o filtro `ng-hide` não remove nenhum resultado nesse caminho. A ordenação por `-popularidade` é aplicada, mas no backend do caminho por sequência não há ordenação explíclica — a ordem depende da coleção filtrada por gênero conforme `apply_filtro` (com popularidade dentro de gênero já ordenada na inicialização).
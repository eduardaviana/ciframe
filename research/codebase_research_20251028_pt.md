# Pesquisa do código-fonte (tal como está) — ciframe/deciframe

## Resumo geral (3-6 frases)
O aplicativo é uma ferramenta de descoberta de músicas (deciframe). O backend é um app Flask em arquivo único (main.py) que carrega o arquivo `data/top/dataset_final.csv` na memória no momento da importação e expõe endpoints JSON (todas as respostas são serializadas com `json.dumps`, retornando `Content-Type: text/html`). A classe `Musica` (musica.py) modela cada música, deriva os acordes como um conjunto de acordes únicos a partir da cifra e gera a URL do Cifraclub. O frontend é AngularJS 1.4.9 com jQuery/Bootstrap carregados via CDN, arquivos estáticos em `static/` (sem etapa de build), com rotas/controladores/diretivas para página inicial, busca por título/artista, busca por acordes e busca por sequências famosas de acordes. Os dados ficam inteiramente em memória (dicionários com chave `id_unico_musica`, listas por gênero ordenadas por popularidade, conjuntos únicos de gêneros/acordes). A API é consumida pelo frontend com `apiUrl` vazio (mesma origem) e endpoints específicos.

## 1) Backend (main.py)
### Carregamento de dados e variáveis globais (inicialização)
- Imports: `json`, `Flask`, `request`, `sys`, `musica.*`, `OrderedDict`, `unicodedata` (main.py:1-7).
- App: `app = Flask(__name__)` (main.py:9).
- `limpa_cifra(raw_cifra)`: filtra tablaturas (linhas contendo `|`) pegando o primeiro token antes de `|` e `split[0]`; caso contrário divide por espaços e concatena tokens. Remove strings vazias (main.py:11-23).
- Constantes das colunas do CSV: `ARTISTA_ID=0`, `MUSICA_ID=1`, `ARTISTA=2`, `MUSICA=3`, `GENERO=4`, `POPULARIDADE=5`, `TOM=6`, `SEQ_FAMOSA=7`, `CIFRA=8`, `TAM_PAGINA=100` (main.py:26-35).
- Globais: `genero_musicas={}`, `generos=set()`, `acordes=set()` (main.py:37-39). `sequencias` mapeia sequências famosas para IDs: `{'BmGDA':0,'CGAmF':1,'EmG':2,'CA7DmG7':3,'GmF':4,'CC7FFm':5}` (main.py:40-45). `musicas_dict={}` (main.py:47).
- Carregamento: `f = open('data/top/dataset_final.csv')`; `f.readline()` para pular cabeçalho (main.py:49-50).
- Para cada linha: remove aspas (`"`) e `NA`, remove último caractere (`[:-1]`) (main.py:53). Divide por `,` (main.py:55). Converte `POPULARIDADE` para int removendo pontos (main.py:56).
- `CIFRA`: se não vazia, `musica[CIFRA] = limpa_cifra(musica[CIFRA].split(';'))`, senão `[]` (main.py:58-61). `SEQ_FAMOSA` dividido por `;` (main.py:63).
- Adiciona gênero ao conjunto `generos` (main.py:66). Cria objeto `Musica` (main.py:69-74) e armazena em `musicas_dict[musica_obj.id_unico_musica]`. Adiciona cada acorde de `musica_obj.acordes` ao conjunto `acordes` (main.py:77-78). Adiciona à lista `genero_musicas[musica_obj.genero]` (main.py:82-85).
- Cria `OrderedDict` ordenado por popularidade decrescente: `musicas = OrderedDict(sorted(musicas_dict.items(), key=lambda x: x[1].popularidade, reverse=True))` (main.py:88-89). `generos = list(generos)` (main.py:92). Ordena cada lista em `genero_musicas` por popularidade decrescente (main.py:95-96). Fecha arquivo (main.py:98).
- Observação: todos os endpoints retornam `json.dumps(...)` como string pura (padrão `Content-Type: text/html`) — comportamento legado intencional (AGENTS.md).

### Rotas/endpoints
- `GET /` (main.py:101-103): retorna `app.send_static_file('index.html')`.
- `GET /<path:path>` (main.py:109-112): proxy estático via `send_static_file`.
- `GET /search` (main.py:114-142):
  - Parâmetros: `generos` (opcional, lista separada por vírgula), `pagina` (padrão `'1'`), `key` (obrigatório).
  - `keys = request.args.get('key').lower()`; `keys = remover_combinantes(keys).split(' ')` (main.py:118-119).
  - `generos_key = generos` se não houver `generos_tag`, senão `generos_tag.split(',')` (main.py:121-123).
  - `collection = apply_filtro(musicas.values(), generos_key)` (main.py:125).
  - Para cada música: `text = '%s %s' % (musica.nome_artista.lower(), musica.nome_musica.lower())`; `text_list = remover_combinantes(text).split(' ')`; se `all(key in text_list for key in keys)`: monta dict com `id_unico_musica`, `id_artista`, `id_musica`, `nome_artista`, `nome_musica`, `genero`, `url` e adiciona (main.py:128-142). Retorna `json.dumps(get_pagina(out, pagina_tag))`.
- `remover_combinantes(string)`: `unicodedata.normalize('NFD', string)` e mantém caracteres com categoria != `'Mn'` (main.py:145-147).
- `GET /musicas` (main.py:154-156): `json.dumps([v.__dict__ for v in musicas.values()])` (todas as músicas ordenadas por popularidade via `OrderedDict`).
- `GET /generos` (main.py:158-160): `json.dumps(generos)`.
- `GET /acordes` (main.py:162-164): `json.dumps(list(acordes))`.
- `GET /musica/<m_id>/` (main.py:166-168): `json.dumps(musicas[m_id].__dict__)`.
- `GET /similares` (main.py:170-201):
  - Parâmetros: `acordes` (lista separada por vírgula), `id_unico_musica`, `sequencia`, `pagina` (padrão `'1'`), `generos` (opcional, lista separada por vírgula).
  - `generos_key = generos` if `generos_tag` else `generos` (main.py:179-183).
  - Se `acordes_tag`: `acordes = acordes_tag.split(',')` (185-187).
  - Senão se `id_musica_tag`: `musica = musicas[id_musica_tag]`; `acordes = musica.acordes` (187-190).
  - Senão se `sequencia_tag`: `acordes = sequencia_tag.replace(',','')`; se `acordes` está em `sequencias`: `id_seq = sequencias[acordes]`; `similares = get_pagina(get_similares_por_sequencia(id_seq, generos_key), pagina_tag)`; retorna `json.dumps(similares)` (190-197).
  - Senão: `similares = get_similares(acordes, generos_key, id_musica_tag)`; retorna `json.dumps(get_pagina(similares, pagina_tag))` (199-201).
- `get_similares_por_sequencia(id_seq, generos_key)` (main.py:203-223): `collection = apply_filtro(musicas.values(), generos_key)`. Para cada música, se `str(id_seq) in musica.seqs_famous` adiciona dict com `id_unico_musica`, `id_artista`, `id_musica`, `nome_artista`, `nome_musica`, `popularidade`, `acordes`, `genero`, `url`.
- `get_pagina(colecao, pagina_tag)` (main.py:226-228): `sl = (int(pagina_tag)-1)*TAM_PAGINA`; retorna `colecao[sl:sl+TAM_PAGINA]`.
- `get_similares(acordes, generos_key, id_musica=None)` (main.py:230-263): `collection = apply_filtro(musicas.values(), generos_key)`. Para cada música onde `musica.id_unico_musica != id_musica`: `inter = set(acordes).intersection(set(musica.acordes))`; `diff = set(musica.acordes)-set(acordes)`; se `len(inter)>0` adiciona dict com `diferenca=list(diff)`, `intersecao=list(inter)`. Ordenado por `(len(diferenca), -len(intersecao))` (main.py:262-263).
- `apply_filtro(musicas, generos_key)` (main.py:266-272): para cada gênero em `generos_key`, se estiver em `generos`, adiciona todas as músicas de `genero_musicas[genero]`.
- CORS: `@app.after_request` adiciona `Access-Control-Allow-Origin: *` (main.py:274-277).
- Execução: `if __name__ == '__main__': app.run(debug=True)` (main.py:279-280).

## 2) Modelo (musica.py)
- Classe `Musica` (musica.py:1-25):
  - `__init__(id_artista, nome_artista, id_musica, nome_musica, genero, popularidade, seqs_famosas, tom, cifra)`: define campos (7-19). `acordes = list(set(cifra))` (acordes únicos). `seqs_famosas` armazenados como estão. `id_unico_musica = '%s_%s' % (id_artista, id_musica)` (20). `url = 'http://www.cifraclub.com.br/%s/%s' % (id_artista, id_musica)` (22).
  - `__str__` retorna `'%s,%s,%s' % (self.id_unico_musica, self.genero, self.popularidade)` (24-25).

## 3) Frontend (static/)
### index.html
- Aplicativo Angular `ng-app="deciframeApp"` (index.html:2). Metatags/OG, título deciframe (1-13). CSS: Bootstrap 3.3.6, Varela Round, `app.css`, `icons.css`, favicon (14-21). Snippet do Google Analytics (25-32). Navbar com logo SVG e botão de menu (`df-hex acorde="?")` (34-88). Container do menu com descrição e equipe (90-121). `ng-view` para páginas (123). Scripts na ordem: jQuery 1.11.3, Bootstrap, Angular 1.4.9, angular-route, angular-animate, ui-bootstrap/js/tpls, `ngprogress.js`, `app.js`, `routes.js`, controllers `main`, `home`, `about`, `acordes`, `musica`, `sequencia`, diretivas `df-hex`, `df-esfinge` (125-148).

### app.js
- Módulo: `angular.module('deciframeApp', ['ngRoute', 'ngAnimate', 'ngProgress', 'ui.bootstrap'])` (app.js:1-2).
- Constante `RESTAPI.url`: `http://localhost:5003` (app.js:3-5) — observação: porta diferente do Docker (8080) / ambiente virtual (5000).
- Constante `GENEROS`: longa lista de nomes de gênero (app.js:6-58).

### routes.js
- Rotas: `'/'` -> `home.html`/`HomeController`; `'/poracordes'` -> `acordes.html`/`AcordesController` (`controllerAs: Chords`); `'/pormusica'` -> `musica.html`/`MusicaController` (`controllerAs: Musica`); `'/porsequencia'` -> `sequencia.html`/`SequeriaController` (na verdade `SequenciaController`, `controllerAs: Sequencia`); `'/sobre'` -> `about.html`/`AboutController`; caso contrário redireciona para `'/''` (routes.js:1-29).

### Controllers
- `MainController` (static/assets/js/controllers/main.js:1-12): alterna `showMenu`, verifica atividade da rota via `route.regexp`.
- `HomeController` (home.js:1-4): define `pageTitle`/`pageClass`.
- `AcordesController` (acordes.js:1-125): define listas de acordes por tonalidade com cores (`acordesC`..`acordesB`). `vm.acordes` contém arrays; `vm.meusAcordes` array. `vm.addAcorde` alterna o acorde em `vm.meusAcordes` e chama `vm.pesquisarPorAcordes()`. `vm.temAcorde` verifica presença. `createChordsString` junta `acordes[].acorde` com vírgulas. `vm.pesquisarPorAcordes()`: se houver acordes, inicia progresso, mensagens, cria `searchString = "similares?acordes=" + string comma`; adiciona `&generos=...` se houver `vm.meuGenero`; chama `$http.get(apiUrl.concat(searchString))` onde `apiUrl` é `""` (linha 91) — mesma origem. Sucesso: `vm.musics = data`, exibe resultados. `vm.goToLirics` abre `music.url`; `vm.goToResults` rola até `#results`.
- `MusicaController` (musica.js:1-80): `vm.getMusicas(val)` chama `apiUrl.concat('search?key='+val)` para sugestões (retorna `response.data`). `vm.pesquisarPorMusica(musica)`: define `vm.minhaMusica`, cria `"similares?id_unico_musica=" + vm.minhaMusica.id_unico_musica` e opcionalmente `&generos=...`; chama `$http.get` na mesma origem. Mesma lógica de resultado.
- `SequenciaController` (sequencia.js:1-105): define 4 sequências famosas (`sequencia1` BmGDA, `sequencia2` CGAmF, `sequencia3` GmF, `sequencia4` CC7FFm) com cores. `vm.sequenciasFamosas` array. `vm.temAcorde` verifica se acorde está em `vm.minhaSequencia.acordes`. `createChordsString` cria string com vírgulas. `vm.pesquisarPorSequencia(sequeria)`: cria `"similares?sequencia=" + string comma`; opcionalmente genero; mesafluxo. `vm.limparPesquisa` limpa seleção.

### Diretivas
- `df-hex` (directives/df-hex.js:1-12): escopo `acorde`, `acordeColor`, `acordeChecked`, `small`; `templateUrl` `templates/directives/df-hex.html`.
- `df-esfinge` referenciada em `index.html`, arquivo não lido anteriormente, mas existe como script.

### Templates (static/templates/)
- Arquivos/pasta: `directives/` contém templates das diretivas, além de `about.html`, `acordes.html',`home.html',`musica.html',`sequencia.html` (listados). Não foram totalmente lidos em detalhes, mas as rotas apontam para eles.

## 4) Dados
- `data/top/dataset_final.csv`: carregado na inicialização (main.py:49). Editar exige reinicialização (AGENTS.md). Estrutura inferida pelo código: CSV com colunas `ARTISTA_ID`, `MUSICA_ID`, `ARTISTA`, `MUSICA`, `GENERO`, `POPULARIDADE`, `TOM`, `SEQ_FAMOSA`, `CIFRA` (processados com `CIFRA/SEQ_FAMOSA` separados por `;`). `POPULARIDADE` pode conter pontos (removidos). Aspas (`"`) e `NA` removidos.

## 5) Configuração/deploy
- `Dockerfile` existe na raiz. README mostra `docker build`/`docker run` mapeando `8080:8080`; `venv` roda na porta `5000`. AGENTS.md afirma que o deploy é apenas local via Docker atualmente; verificar `docs/adr/` antes de alterar o setup de deploy.
- `requirements.txt` presente. `.dockerignore`, `.gitignore` presente.
- `docs/adr/` contém ADRs (mencionado em AGENTS.md). `research/` existe.

## Fluxos entre componentes / fluxo de dados
1. Inicialização: Flask importa `main.py` -> lê CSV -> cria objetos `Musica` -> popula `musicas_dict`, `musicas` (`OrderedDict` por popularidade), `genero_musicas` (listas por gênero ordenadas), `generos`, `acordes`. Apenas em memória.
2. Frontend carrega `index.html` -> `app.js` define módulo/constantes (`RESTAPI.url` `http://localhost:5003` mas as portas reais diferem; controllers usam `apiUrl` vazio para mesma origem). Rotas carregam templates/controladores.
3. Fluxos de usuário:
- Por acordes (`/poracordes`): seleciona acordes via `df-hex` -> `AcordesController.addAcorde` alterna em `vm.meusAcordes` -> `pesquisarPorAcordes()` faz `GET /similares?acordes=...[,generos=...]` -> backend `get_similares` filtra por gênero (`apply_filtro` em `musicas.values()`), calcula interseção entre conjuntos de acordes com `musica.acordes` (conjunto único), exclui mesma música se `id_musica_tag` passado, ordena por `(len(diferenca), -len(intersecao))`, pagina -> retorna lista com `diferenca`, `intersecao`, `popularidade`, `acordes`, `genero',`url'.
- Por música (`/pormusica`): sugestões via `getMusicas()` `GET /search?key=...` (backend busca case-insensitive por substring em artista+título concatenados após remover diacríticos, todas as `keys` devem estar presentes nos tokens separados), seleciona música -> `pesquisarPorMusica()` `GET /similares?id_unico_musica=...` -> backend usa `musica.acordes` como referência (exclui mesma música), mesmo mecanismo de similaridade.
- Por sequência (`/porsequencia`): seleciona uma das 4 sequências famosas -> `pesquisarPorSequencia()` `GET /similares?sequencia=BmGDA,...` (backend junta sem vírgula: `sequencia_tag.replace(',','')') -> backend verifica mapa `sequencias`, chama `get_similares_por_sequencia(id_seq, generos_key)`, encontra músicas onde `str(id_seq) in musica.seqs_famosas`.
4. Todas as respostas são strings `json.dumps`; frontend consume JSON via `$http`. CORS habilitado globalmente.

## Referências concretas de arquivos e linhas (principais)
- `main.py:1-280` (imports, carregamento, rotas, similaridade/paginação/filtro)
- `musica.py:1-25` (modelo `Musica`)
- `static/index.html:1-149` (shell, scripts)
- `static/assets/js/app.js:1-58` (módulo, constantes)
- `static/assets/js/routes.js:1-29` (rotas)
- `static/assets/js/controllers/main.js:1-12; home.js:1-4; acordes.js:1-125; musica.js:1-80; sequencia.js:1-105`
- `static/assets/js/directives/df-hex.js:1-12`
- `static/templates/` (`about.html`, `acordes.html',`home.html',`musica.html',`sequencia.html`, `directives/`)
- `data/top/dataset_final.csv` (referenciado)
- `AGENTS.md`, `README.md`, `requirements.txt`, `Dockerfile`

## Observações (apenas tal como está)
- `RESTAPI.url` em `app.js` aponta para `http://localhost:5003` mas README/Docker indicam `8080` (Docker) ou `5000` (venv); controllers usam `apiUrl` vazio (`""`) conforme código atual, ou seja, requisições são feitas na mesma origem.
- Mapa de sequências famosas no backend: chaves são strings concatenadas sem separadores (`BmGDA`, `CGAmF`, `EmG`, `CA7DmG7`, `GmF`, `CC7FFm`). Frontend `sequencia1` usa `Bm`, `G`, `D`, `A` (juntados como `Bm,G,D,A` em `createChordsString`) e envia `sequencia=B,M,G,D,A`? Na verdade envia `sequencia=Bm,G,D,A` que o backend converte com `replace(',','')` para bater com o mapa.
- `musica.acordes` é lista de acordes únicos (`set`). Similaridade usa interseção/diferença de conjuntos (`set`) sobre `acordes`.
- `/musicas` retorna `__dict__ completo das todas as músicas ordenadas por popularidade (`OrderedDict`). `/search` faz busca por token com remoção de diacríticos, case-insensitive, exigindo que todas as palavras-chave estejam presentes nos tokens (artista+título concatenados).
- Paginação via `get_pagina` com `TAM_PAGINA=100`.

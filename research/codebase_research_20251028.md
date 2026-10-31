# Codebase research (as-is) — ciframe/deciframe

## High-level summary (3-6 sentences)
The app is a song-discovery tool (deciframe). Backend is a single-file Flask app (main.py) that loads data/top/dataset_final.csv into memory at import time and exposes JSON endpoints (all responses serialized with json.dumps, returning text/html). A Musica class (musica.py) models each song and derives acordes as a set of unique chords from cifra and builds a Cifraclub URL. Frontend is AngularJS 1.4.9 with jQuery/Bootstrap loaded from CDN, static files under static/ (no build step), with routes/controllers/directives for home, search by song title/artist, search by chords, and search by famous chord sequences. Data is fully in-memory (dicts keyed by id_unico_musica, per-genre lists sorted by popularity, unique sets of genres/acordes). The API is consumed by frontend with hardcoded apiUrl "" (same origin) and specific endpoints.

## 1) Backend (main.py)
### Data loading and globals (startup)
- Imports: json, Flask, request, sys, musica.*, OrderedDict, unicodedata (main.py:1-7).
- App: app = Flask(__name__) (main.py:9).
- limpa_cifra(raw_cifra): splits by semicolons not shown here; it filters tablatures lines containing '|' taking first token before '|' and split[0], otherwise splits by whitespace and concatenates tokens. Filters empty strings (main.py:11-23).
- CSV column constants: ARTISTA_ID=0, MUSICA_ID=1, ARTISTA=2, MUSICA=3, GENERO=4, POPULARIDADE=5, TOM=6, SEQ_FAMOSA=7, CIFRA=8, TAM_PAGINA=100 (main.py:26-35).
- Globals: genero_musicas={}, generos=set(), acordes=set() (main.py:37-39). sequencias maps famous sequences to ids: {'BmGDA':0,'CGAmF':1,'EmG':2,'CA7DmG7':3,'GmF':4,'CC7FFm':5} (main.py:40-45). musicas_dict={} (main.py:47).
- Load: f = open('data/top/dataset_final.csv'); f.readline() to skip header (main.py:49-50).
- For each line: replace '"' and 'NA' and strip trailing char ([:-1]) (main.py:53). split by ',' (main.py:55). POPULARIDADE converted to int after removing dots (main.py:56).
- CIFRA: if non-empty, musica[CIFRA] = limpa_cifra(musica[CIFRA].split(';')) else [] (main.py:58-61). SEQ_FAMOSA split by ';' (main.py:63).
- Add genero to generos set (main.py:66). Create Musica(musica[ARTISTA_ID], musica[ARTISTA], musica[MUSICA_ID], musica[MUSICA], musica[GENERO], int(musica[POPULARIDADE]), musica[SEQ_FAMOSA], musica[TOM], musica[CIFRA]) and store in musicas_dict[musica_obj.id_unico_musica] (main.py:69-74). Add each acorde in musica_obj.acordes to acordes set (main.py:77-78). Append to genero_musicas[musica_obj.genero] list (main.py:82-85).
- Build ordered dict by popularity desc: musicas = OrderedDict(sorted(musicas_dict.items(), key=lambda x: x[1].popularidade, reverse=True)) (main.py:88-89). generos = list(generos) (main.py:92). Sort each genero_musicas list by popularidade desc (main.py:95-96). Close file (main.py:98).
- Note: all endpoints return json.dumps(...) as plain string (Content-Type text/html by default) — intentional legacy behavior (AGENTS.md).

### Routes/endpoints
- GET / (main.py:101-103): returns app.send_static_file('index.html').
- GET /<path:path> (main.py:109-112): static proxy via send_static_file.
- GET /search (main.py:114-142): 
  - params: generos (optional comma list), pagina (default '1'), key (required). 
  - keys = request.args.get('key').lower(); keys = remover_combinantes(keys).split(' ') (main.py:118-119).
  - generos_key = generos if no generos_tag else generos_tag.split(',') (main.py:121-123).
  - collection = apply_filtro(musicas.values(), generos_key) (main.py:125).
  - For each musica: text = '%s %s' % (musica.nome_artista.lower(), musica.nome_musica.lower()); text_list = remover_combinantes(text).split(' '); if all(key in text_list for key in keys): build match dict with id_unico_musica, id_artista, id_musica, nome_artista, nome_musica, genero, url; append (main.py:128-142). Returns json.dumps(get_pagina(out, pagina_tag)).
- remover_combinantes(string): unicodedata.normalize('NFD', string) and keep chars where category != 'Mn' (main.py:145-147).
- GET /musicas (main.py:154-156): returns json.dumps([v.__dict__ for v in musicas.values()]) (all songs ordered by popularity via OrderedDict).
- GET /generos (main.py:158-160): json.dumps(generos).
- GET /acordes (main.py:162-164): json.dumps(list(acordes)).
- GET /musica/<m_id>/ (main.py:166-168): returns json.dumps(musicas[m_id].__dict__).
- GET /similares (main.py:170-201):
  - params: acordes (comma list), id_unico_musica, sequencia, pagina (default '1'), generos (optional comma list).
  - generos_key = generos if generos_tag else generos (main.py:179-183).
  - if acordes_tag: acordes = acordes_tag.split(',') (185-187).
  - elif id_musica_tag: musica = musicas[id_musica_tag]; acordes = musica.acordes (187-190).
  - elif sequencia_tag: acordes = sequencia_tag.replace(',',''); if acordes in sequencias: id_seq = sequencias[acordes]; similares = get_pagina(get_similares_por_sequencia(id_seq, generos_key), pagina_tag); return json.dumps(similares) (190-197).
  - else: similares = get_similares(acordes, generos_key, id_musica_tag); return json.dumps(get_pagina(similares, pagina_tag)) (199-201).
- get_similares_por_sequencia(id_seq, generos_key) (main.py:203-223): collection = apply_filtro(musicas.values(), generos_key); for each musica if str(id_seq) in musica.seqs_famosas append match dict with id_unico_musica,id_artista,id_musica,nome_artista,nome_musica,popularidade,acordes,genero,url.
- get_pagina(colecao, pagina_tag): sl = (int(pagina_tag)-1)*TAM_PAGINA; return colecao[sl:sl+TAM_PAGINA] (main.py:226-228).
- get_similares(acordes, generos_key, id_musica=None) (main.py:230-263): collection = apply_filtro(musicas.values(), generos_key); for each musica where musica.id_unico_musica != id_musica: compute inter = set(acordes).intersection(set(musica.acordes)); diff = set(musica.acordes)-set(acordes); if len(inter)>0 append dict including diferenca=list(diff), intersecao=list(inter). Sorted by (len(diferenca), -len(intersecao)) (main.py:262-263).
- apply_filtro(musicas, generos_key): for each genero in generos_key if genero in generos add all genero_musicas[genero] (main.py:266-272).
- CORS: @app.after_request adds Access-Control-Allow-Origin: * (main.py:274-277).
- Run: if __name__ == '__main__': app.run(debug=True) (main.py:279-280).

## 2) Model (musica.py)
- class Musica (musica.py:1-25):
  - __init__(id_artista, nome_artista, id_musica, nome_musica, genero, popularidade, seqs_famosas, tom, cifra): sets fields (7-19). acordes = list(set(cifra)) (unique chords). seqs_famosas stored as-is. id_unico_musica = '%s_%s' % (id_artista, id_musica) (20). url = 'http://www.cifraclub.com.br/%s/%s' % (id_artista, id_musica) (22).
  - __str__ returns '%s,%s,%s' % (self.id_unico_musica, self.genero, self.popularidade) (24-25).

## 3) Frontend (static/)
### index.html
- Angular app ng-app="deciframeApp" (index.html:2). Meta tags/OG, title deciframe (1-13). CSS: Bootstrap 3.3.6, Varela Round, app.css, icons.css, favicon (14-21). GA snippet (25-32). Navbar with brand logo SVG and menu toggle (df-hex acorde="?") (34-88). Menu container with description and team (90-121). ng-view for pages (123). Scripts loaded in order: jQuery 1.11.3, Bootstrap, Angular 1.4.9, angular-route, angular-animate, ui-bootstrap/js/tpls, ngprogress.js, app.js, routes.js, controllers/main/home/about/acordes/musica/sequencia, directives df-hex/df-esfinge (125-148).

### app.js
- Module: angular.module('deciframeApp', ['ngRoute', 'ngAnimate', 'ngProgress', 'ui.bootstrap']) (app.js:1-2).
- Constant RESTAPI.url: 'http://localhost:5003' (app.js:3-5) — note different port than Docker (8080) / venv (5000).
- Constant GENEROS: long list of genre names (app.js:6-58).

### routes.js
- Routes: '/' -> home.html/HomeController; '/poracordes' -> acordes.html/AcordesController (controllerAs Chords); '/pormusica' -> musica.html/MusicaController (Musica); '/porsequencia' -> sequencia.html/SequenciaController (Sequencia); '/sobre' -> about.html/AboutController; otherwise redirect '/' (routes.js:1-29).

### Controllers
- MainController (static/assets/js/controllers/main.js:1-12): $scope.showMenu toggle, isActive checks route regexp.
- HomeController (home.js:1-4): sets pageTitle/pageClass.
- AcordesController (acordes.js:1-125): defines chord lists by root with colors (acordesC..acordesB). vm.acordes contains arrays; vm.meusAcordes array. vm.addAcorde toggles chord in vm.meusAcordes and calls vm.pesquisarPorAcordes(). vm.temAcorde checks membership. createChordsString joins acordes[].acorde with commas. vm.pesquisarPorAcordes(): if vm.meusAcordes.length, starts progress, sets messages, builds searchString = "similares?acordes=" + comma string; if vm.meuGenero adds &generos=...; calls $http.get(apiUrl.concat(searchString)) where apiUrl is "" (line 91) — same origin. On success sets vm.musics = data, shows results. vm.goToLirics opens music.url; vm.goToResults scrolls to #results.
- MusicaController (musica.js:1-80): vm.getMusicas(val) calls apiUrl.concat('search?key='+val) for typeahead/search suggestions (returns response.data). vm.pesquisarPorMusica(musica): sets vm.minhaMusica, builds "similares?id_unico_musica="+vm.minhaMusica.id_unico_musica plus optional genero; calls same-origin $http.get. Same result handling as AcordesController.
- SequenciaController (sequencia.js:1-105): defines 4 famous sequences (sequencia1 BmGDA, sequencia2 CGAmF, sequencia3 GmF, sequencia4 CC7FFm) with colors. vm.sequenciasFamosas array. vm.temAcorde checks if acorde in vm.minhaSequencia.acordes. createChordsString builds comma string. vm.pesquisarPorSequencia(sequencia): builds "similares?sequencia=" + comma string; optional genero; same flow. vm.limparPesquisa clears selection.

### Directives
- df-hex (directives/df-hex.js:1-12): scope acorde, acordeColor, acordeChecked, small; templateUrl templates/directives/df-hex.html.
- df-esfinge referenced in index.html but file not listed in templates/directives read earlier; exists as script include.

### Templates (static/templates/)
- Directories/files: directives/ contains templates for directives (df-hex.html etc.), plus about.html, acordes.html, home.html, musica.html, sequencia.html (listed). Not fully read in detail, but routes point to them.

## 4) Data
- data/top/dataset_final.csv: loaded at startup (main.py:49). Editing requires restart (AGENTS.md). Structure inferred from code: CSV with columns ARTISTA_ID, MUSICA_ID, ARTISTA, MUSICA, GENERO, POPULARIDADE, TOM, SEQ_FAMOSA, CIFRA (semicolon-separated in CIFRA/SEQ_FAMOSA in processing). POPULARIDADE may have dots (removed). NA and quotes stripped.

## 5) Config/deploy
- Dockerfile exists (repo root). README shows docker build/run mapping 8080:8080; venv runs on 5000. AGENTS.md states deploy is local-only via Docker for now; check docs/adr before changing deploy.
- requirements.txt present. .dockerignore, .gitignore present.
- docs/adr/ contains ADRs (mentioned in AGENTS.md). research/ directory exists.

## Cross-component connections / data flows
1. Startup: Flask imports main.py -> reads CSV -> builds Musica objects -> populates musicas_dict, musicas (OrderedDict by popularity), genero_musicas (per genre lists sorted), generos list, acordes set. In-memory only.
2. Frontend loads index.html -> app.js defines module/constants (RESTAPI.url http://localhost:5003 in app.js but actual server ports differ; controllers use apiUrl "" so same-origin). Routes load templates/controllers.
3. User flows:
- Por acordes (/poracordes): select chords via df-hex -> AcordesController.addAcorde toggles in vm.meusAcordes -> pesquisarPorAcordes() GET /similares?acordes=...[,generos=...] -> backend get_similares filters by genre (apply_filtro on musicas.values()), finds intersection of chord sets with musica.acordes (unique set), excludes same song if id_musica_tag passed, sorts by (len(diferenca), -len(intersecao)), paginates -> returns list with diferenca/intersecao/popularidade/acordes/genero/url.
- Por música (/pormusica): typeahead via getMusicas() GET /search?key=... (backend does case-insensitive substring match on concatenated artist+title after removing diacritics, all keys must be present in split tokens), select song -> pesquisarPorMusica() GET /similares?id_unico_musica=... -> backend takes musica.acordes as reference (excludes same song), same similarity logic.
- Por sequência (/porsequencia): select one of 4 famous sequences -> pesquisarPorSequencia() GET /similares?sequencia=BmGDA,... (joined without comma in backend: sequencia_tag.replace(',','')) -> backend checks sequencias map, calls get_similares_por_sequencia(id_seq, generos_key) which finds songs where str(id_seq) in musica.seqs_famosas.
4. All responses are json.dumps strings; frontend consumes as JSON via $http. CORS enabled globally.

## Concrete file paths and line references (key)
- main.py:1-280 (imports, loading, routes, similarity/pagination/filter)
- musica.py:1-25 (Musica model)
- static/index.html:1-149 (shell, scripts)
- static/assets/js/app.js:1-58 (module, constants)
- static/assets/js/routes.js:1-29 (routes)
- static/assets/js/controllers/main.js:1-12; home.js:1-4; acordes.js:1-125; musica.js:1-80; sequencia.js:1-105
- static/assets/js/directives/df-hex.js:1-12
- static/templates/ (about.html, acordes.html, home.html, musica.html, sequencia.html, directives/)
- data/top/dataset_final.csv (referenced)
- AGENTS.md, README.md, requirements.txt, Dockerfile

## Notes (as-is only)
- RESTAPI.url in app.js points to http://localhost:5003 but README/Docker indicate 8080 (Docker) or 5000 (venv); controllers use empty apiUrl string (same origin) in the code as written.
- Famous sequences in backend map: keys are concatenated chord strings without separators (BmGDA, CGAmF, EmG, CA7DmG7, GmF, CC7FFm). Frontend sequencia1 uses Bm,G,D,A (joined as Bm,G,D,A in createChordsString) and sends as sequencia=Bm,G,D,A which backend converts by replace(',','') to match map.
- musica.acordes is list of unique chords (set). Similarity uses set intersection/difference on acordes.
- /musicas returns full __dict__ of all songs ordered by popularity (OrderedDict). /search does tokenized diacritic-insensitive match on artist+title requiring all keys.
- Pagination via get_pagina with TAM_PAGINA=100.

# Mecanismo das sequências famosas: como funciona na prática

## Resumo (3-6 frases)
A detecção de "sequência famosa" **não é feita por busca de subsequência na cifra no momento da requisição**. O código não varre a lista de acordes da música para ver se aparece `Bm,G,D,A` em ordem seguida. Em vez disso, o CSV já traz uma **tag pré-computada** na coluna `SEQ_FAMOSA` (índice 7). No carregamento (`main.py:49-64`), essa coluna é dividida por `;` e armazenada em `Musica.seqs_famosas` (`musica.py:18`). No endpoint `GET /similares` com `?sequencia=...`, o backend apenas mapeia a string concatenada (enviada pelo frontend, ex. `Bm,G,D,A` → `BmGDA`) para um ID numérico via o mapa hardcoded `sequencias` (`main.py:40-45`), chama `get_similares_por_sequencia(id_seq, generos_key)` e filtra por `str(id_seq) in musica.seqs_famosas` (`main.py:194-197, 203-223`). Não há verificação de "aparecer seguida", não há busca por padrão, não há normalização.

## 1) O mapa hardcoded
Em `main.py:40-45`:
```python
sequencias = {'BmGDA' : 0,
        'CGAmF' : 1,
        'EmG' : 2,
        'CA7DmG7' : 3,
        'GmF' : 4,
        'CC7FFm' : 5}
```
Chaves são **concatenações sem separadores** dos nomes dos acordes das 6 sequências famosas definidas no front-end (`static/assets/js/controllers/sequencia.js:2-37`).

## 2) Como a tag chega e é armazenada
No carregamento (`main.py:49-98`):
- `main.py:50`: `f.readline()` para pular cabeçalho.
- `main.py:53`: linha limpa com `line.replace('"', '').replace('NA', '')[:-1]`.
- `main.py:55`: `musica = line.split(',')`.
- `main.py:58-61`: `CIFRA` processada com `limpa_cifra(musica[CIFRA].split(';'))` se não vazia.
- `main.py:63`: `musica[SEQ_FAMOSA] = musica[SEQ_FAMOSA].split(";")` — **a tag já vem pré-computada no CSV**.
- `main.py:69-74`: cria `Musica(musica[ARTISTA_ID], ..., musica[SEQ_FAMOSA], musica[TOM], musica[CIFRA])`.
- `musica.py:5,18`: `self.seqs_famosas = seqs_famosas` guarda a lista exatamente como veio (após split por `;`).

### Exemplos do CSV (como está)
Com encoding `utf-8`:
- Linha ~135: artista `30 Seconds To Mars`, música `City Of Angels`, `seq_famosa: 0`, cifra começa com `D;A;Bm;G;D;A;Bm;G;...` (muitos acordes)
- Linha ~204: artista `5 Seconds Of Summer`, música `Bad Dreams`, `seq_famosa: 1`, `cifra first 30: ['C', 'F', 'Am', 'G', 'C', 'C', 'F', 'F', 'C', 'C', 'F', 'F', 'G', 'F', 'G', 'F', 'C', 'G', 'Am', 'F', 'C', 'G', 'Am', 'F', 'G', 'C']` (aparece `C','F','Am','G' nas primeiras posições, mas tag é `1` que corresponde a `CGAmF`)
- Linha ~4393: artista `Asa de Águia`, música `Marajá`, `seq_famosa: 4`, `cifra first 40: ['Gm', 'F', 'Gm', 'F']` (tag `4` corresponde a `GmF` e na cifra vemos `Gm','F','Gm','F'` — aparece, mas não é por busca no momento da requisição)

Esses exemplos mostram que a tag existe como valor numérico (`0`,`1`,`4`), separado por `;` se houver múltiplos valores. O fato de aparecerem os acordes da sequência em algum lugar na cifra **não significa que o código faz essa busca**; significa que **a tag foi pré-computada** (provavelmente em algum processo anterior fora do runtime atual).

## 3) Como o front-end envia e como o back-end processa
Front-end `SequenciaController` (`static/assets/js/controllers/sequencia.js:2-105`):
- Define 4 sequências famosas com objetos de acordes (sequencia1 = `[Bm,G,D,A]`, sequencia2 = `[C,G,Am,F]`, sequencia3 = `[Gm,F]`, sequencia4 = `[C,C7,F,Fm]`) (`static/assets/js/controllers/sequencia.js:2-38`).
- `createChordsString` junta com vírgula (`static/assets/js/controllers/sequencia.js:55-61`).
- `vm.pesquisarPorSequencia(sequencia)` monta `similares?sequencia=` com essa string e adiciona gênero se houver, faz `$http.get` (`static/assets/js/controllers/sequencia.js:63-90`).

Back-end `GET /similares` (`main.py:170-201`):
- `main.py:175`: lê `sequencia_tag`.
- `main.py:190-197`: se `sequencia_tag` existir, `acordes = sequencia_tag.replace(',','')` (remove vírgulas). Se `acordes` estiver em `sequencias` (`main.py:194-195`), obtém `id_seq = sequencias[acordes]` (0-5). Chama `get_pagina(get_similares_por_sequencia(id_seq, generos_key), pagina_tag)` (`main.py:196`) e retorna `json.dumps(similares)` (`main.py:197`).

## 4) Filtragem por tag pré-computada
`get_similares_por_sequencia(id_seq, generos_key)` (`main.py:203-223`):
- `main.py:205`: `collection = apply_filtro(musicas.values(), generos_key)` (`main.py:266-272`).
- `main.py:208-222`: para cada música na coleção, `if str(id_seq) in musica.seqs_famosas:` (`main.py:209`) adiciona um objeto sem `diferenca`/`intersecao` (`main.py:210-221`). Sem `sorted()`.
- A lista `musica.seqs_famosas` é exatamente a lista vinda do CSV após `split(';')` (`main.py:63`), armazenada em `Musica.seqs_famosas` (`musica.py:18`).

## Resposta direta à pergunta
**Não precisa aparecer "seguida" em um trecho específico. Não existe esse mecanismo no código atual.** 

O back-end **não** analisa a ordem da cifra da música. Ele simplesmente verifica **membership**: `str(id_seq) in musica.seqs_famosas`. A tag `SEQ_FAMOSA` é pré-computada no CSV. O fato de, em exemplos, a sequência de acordes aparecer na cifra não é consequência de uma busca por subsequência realizada pelo `main.py` na hora da requisição; é o dado pré-existente. Não há `find`, não hay substring/sequence matching dinâmico sobre `musica.cifra` ou sobre `musica.acordes`, não há normalização e não há verificação de posição/continuidade.

## Referências concretas
- `main.py:40-45` (mapa `sequencias`)
- `main.py:49-64` (carregamento CSV: `CIFRA` e `SEQ_FAMOSA`)
- `main.py:170-197` (roteamento `/similares` por `sequencia`)
- `main.py:203-223` (`get_similares_por_sequencia`)
- `main.py:266-272` (`apply_filtro`)
- `musica.py:5,16-18` (armazenamento `cifra`, `acordes`, `seqs_famosas`)
- `static/assets/js/controllers/sequencia.js:2-105` (envio da sequência concatenada com vírgula)
- `data/top/dataset_final.csv` (coluna 7 = `SEQ_FAMOSA`; exemplos linha ~135 seq 0, ~204 seq 1, ~4393 seq 4)
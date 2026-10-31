# Normalização de acordes — estado atual (as-is)

## Resumo (3-6 frases)
Não existe normalização de acordes no código-fonte atual. A única normalização de texto existente é `remover_combinantes()` em `main.py:145-147`, que utiliza `unicodedata.normalize('NFD')` para remover diacríticos, sendo utilizada **apenas** na rota `/search` para busca por título/artista. Para cifras e acordes, `limpa_cifra()` (`main.py:11-23`) realiza apenas extração e filtragem de tablaturas, sem qualquer conversão entre enarmônicos (`#` <-> `b`), padronização de caixa ou normalização de sufixos. Em `musica.py:17`, `self.acordes = list(set(cifra))` armazena os acordes exatamente como vieram após `limpa_cifra()`. Todas as comparações no caminho por acordes (`get_similares`, `main.py:240-241`) e no caminho por sequência famosa (`sequencias`, `main.py:40-45`, `main.py:194`, `main.py:209`) são feitas com **strings exatas**.

## 1) Única normalização existente: diacríticos para busca por texto
Em `main.py:145-147` existe:

```python
def remover_combinantes(string):
    string = unicodedata.normalize('NFD', string)
    return u''.join(ch for ch in string if unicodedata.category(ch) != 'Mn')
```

É utilizada exclusivamente em `/search` (`main.py:114-142`):

- `main.py:118-119`: `keys = request.args.get('key').lower(); keys = remover_combinantes(keys).split(' ')`
- `main.py:129-131`: `text = '%s %s' % (musica.nome_artista.lower(), musica.nome_musica.lower()); text_list = remover_combinantes(text).split(' '); if all(key in text_list for key in keys): ...`

**Motivo (conforme código):** remover acentos/diacríticos para permitir busca case-insensitive por substring em `nome_artista + nome_musica`. Não há qualquer relação com acordes/cifras.

## 2) Processamento de cifras e acordes

### Extração com `limpa_cifra`
`limpa_cifra(raw_cifra)` (`main.py:11-23`):

```python
def limpa_cifra(raw_cifra):
    cifra = []
    for m in raw_cifra:
        if m.strip() != '':
            # filtra tablaturas
            if '|' in m:
                acorde = m.split('|')[0].split()[0]
                cifra.append(acorde)
            # lida com acordes separados por espaço
            else:
                tokens = [token for token in m.split()]
                cifra += tokens
    return cifra
```

No carregamento do CSV (`main.py:49-64`):
- `main.py:58-61`: se `musica[CIFRA] != ''`, `musica[CIFRA] = limpa_cifra(musica[CIFRA].split(';'))` senão `[]`.
- `main.py:63`: `musica[SEQ_FAMOSA] = musica[SEQ_FAMOSA].split(";")`

**O que faz:** filtra linhas com `|` pegando apenas o primeiro token antes de `|` ou divide por espaços quando não há `|`. Remove strings vazias. **Não** normaliza acordes.

### Armazenamento
Em `musica.py:5,17-18`:
```python
self.cifra = cifra
self.acordes = list(set(cifra))
self.seqs_famosas = seqs_famosas
```

`self.acordes = list(set(cifra))` armazena os acordes como **acordes únicos**, exatamente na forma em que ficaram após `limpa_cifra()`. Não há transformação alguma.

## 3) Comparações são exatas (sem normalização)

### Caminho por acordes / por música
Frontend "Por acordes" (`/poracordes`): `static/assets/js/controllers/acordes.js:63-97`
- `vm.addAcorde` adiciona/remove acordes em `vm.meusAcordes` (`static/assets/js/controllers/acordes.js:63-75`)
- `vm.pesquisarPorAcordes()` monta `similares?acordes=` com `createChordsString` juntando com vírgula (`static/assets/js/controllers/acordes.js:76-97`). Os acordes são enviados **exatamente** como strings.

Backend `GET /similares` (`main.py:170-201`):
- `main.py:173,185-187`: se vier `acordes_tag`, `acordes = acordes_tag.split(',')` (sem normalização)
- `main.py:174,187-190`: se vier `id_unico_musica`, `musica = musicas[id_musica_tag]`; `acordes = musica.acordes` (acordes únicos da música, exatos)
- `main.py:199-201`: segue para `get_similares(acordes, generos_key, id_musica_tag)`

Em `get_similares` (`main.py:230-263`):
```python
inter = set(acordes).intersection(set(musica.acordes))
diff = set(musica.acordes) - set(acordes)
...
if len(inter) > 0:
    ...
```
(`main.py:240-241,245`)

A interseção e diferença são feitas com `set()` de strings **exatas**. Não existe código para tratar equivalentes enarmônicos.

### Caminho por sequência famosa
`main.py:40-45`:
```python
sequencias = {'BmGDA' : 0,
        'CGAmF' : 1,
        'EmG' : 2,
        'CA7DmG7' : 3,
        'GmF' : 4,
        'CC7FFm' : 5}
```

`GET /similares` (`main.py:190-197`):
- `main.py:191`: `acordes = sequencia_tag.replace(',','')` (apenas remoção de vírgulas)
- `main.py:194-196`: `if acordes in sequencias: id_seq = sequencias[acordes]` então chama `get_similares_por_sequencia(id_seq, generos_key)`

`get_similares_por_sequencia` (`main.py:203-223`):
- `main.py:209`: `if str(id_seq) in musica.seqs_famosas:` onde `musica.seqs_famosas` vem do CSV pré-processado (`main.py:63`) e armazenado em `Musica` (`musica.py:18`)

Tudo por **igualdade exata** de string/valor.

## Exemplo concreto
Se uma música tiver `self.acordes = ['Bb', 'F']` (após `limpa_cifra`) e o usuário selecionar `A#` e `F` na tela "Por acordes", a requisição será `?acordes=A#,F`. Em `get_similares` (`main.py:240`), `set(['A#','F']).intersection(set(['Bb','F']))` resultará apenas em `{'F'}`, pois `'A#'` != `'Bb'`. Não existe código para normalizar `A#` para `Bb` ou vice-versa, portanto essa música **não** será considerada como tendo o acorde `A#` em comum com a busca.

## Referências concretas
- `main.py:11-23` (`limpa_cifra`)
- `main.py:40-45` (mapa `sequencias`)
- `main.py:49-64` (carregamento CSV: `CIFRA` e `SEQ_FAMOSA`)
- `main.py:118-119,129-131,145-147` (`remover_combinantes` apenas em `/search`)
- `main.py:170-201,230-263` (`/similares` por acordes/música)
- `main.py:190-197,203-223` (`/similares` por sequência famosa)
- `musica.py:5,17-18` (armazenamento de `acordes` e `seqs_famosas`)
- `static/assets/js/controllers/acordes.js:63-97` (envio dos acordes selecionados)

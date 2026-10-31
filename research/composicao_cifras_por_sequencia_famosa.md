# Composição das cifras por sequência famosa (dataset_final.csv)

## Resumo (3-6 frases)
Com base na inspeção do `data/top/dataset_final.csv`, para **todas** as músicas marcadas com as 6 sequências famosas (SEQ_FAMOSA = `0`-`5`), o conjunto **único** de acordes da cifra (`row[8]` dividido por `;`) é **subconjunto** exato do conjunto de acordes da sequência mapeada em `main.py:40-45`. Ou seja, as músicas com tag de sequência famosa usam **apenas** os acordes daquela sequência (sem outros acordes), mas **não necessariamente na ordem** da chave concatenada. A ordem não é verificada pelo código em tempo de execução — o `main.py` apenas filtra por membership na tag pré-computada (`main.py:63`, `musica.py:18`, `main.py:209`). A atribuição da tag foi feita em processo prévio ao runtime.

## Mapeamento (conforme código)
`main.py:40-45`:
```python
sequencias = {'BmGDA' : 0,
        'CGAmF' : 1,
        'EmG' : 2,
        'CA7DmG7' : 3,
        'GmF' : 4,
        'CC7FFm' : 5}
```
Conjuntos de acordes da sequência (ordem da chave não é relevante para a composição):
- SEQ 0 (`BmGDA`) → {A, Bm, D, G}
- SEQ 1 (`CGAmF`) → {Am, C, F, G}
- SEQ 2 (`EmG`) → {Em, G}
- SEQ 3 (`CA7DmG7`) → {A7, C, Dm, G7}
- SEQ 4 (`GmF`) → {F, Gm}
- SEQ 5 (`CC7FFm`) → {C, C7, F, Fm}

## Exemplos inspecionados

### SEQ 0 = BmGDA (apenas {A,Bm,D,G})
- 30 Seconds To Mars - City Of Angels → `song_unique = ['A', 'Bm', 'D', 'G']`, `only_seq_chords = True`
- 5 Seconds Of Summer - Heartache On The Big Screen → `['A', 'Bm', 'D', 'G']`, `True`
- 5 Seconds Of Summer - Independence Day → `['A', 'Bm', 'D', 'G']`, `True`
- ABBA - Hey Hey Helen → `['A', 'Bm', 'D', 'G']`, `True`

### SEQ 1 = CGAmF (apenas {Am,C,F,G})
- 5 Seconds Of Summer - Bad Dreams → `['Am', 'C', 'F', 'G']`, `True`
- 5 Seconds Of Summer - Broken Pieces → `['Am', 'C', 'F', 'G']`, `True`
- 5 Seconds Of Summer - Fly Away → `['Am', 'C', 'F', 'G']`, `True`
- 5 Seconds Of Summer - Lost Boy → `['Am', 'C', 'F', 'G']`, `True`

### SEQ 2 = EmG (apenas {Em,G})
- Eric Clapton - Fall Like Rain → `['Em', 'G']`, `True`
- Marcelo D2 - Mão Na Cabeça → `['Em', 'G']`, `True`
- Planet Hemp - Mão Na Cabeça → `['Em', 'G']`, `True`
- Ultraje a Rigor - Inútil → `['Em', 'G']`, `True`

### SEQ 3 = CA7DmG7 (apenas {A7,C,Dm,G7})
- Arlindo Cruz - Vai Pro Lado de Cá → `['A7', 'C', 'Dm', 'G7']`, `True`
- Benito Di Paula - Bendito Seja → `['A7', 'C', 'Dm', 'G7']`, `True`
- Bezerra da Silva - Na Aba → `['A7', 'C', 'Dm', 'G7']`, `True`
- Dorival Caymmi - Requebre que Eu Dou um Doce → `['A7', 'C', 'Dm', 'G7']`, `True`

### SEQ 4 = GmF (apenas {F,Gm})
- Asa de Águia - Marajá → `['F', 'Gm']`, `True`
- Aviões do Forró - Piriri Pom Pom → `['F', 'Gm']`, `True`
- Oriente - Feito → `['F', 'Gm']`, `True`

### SEQ 5 = CC7FFm (apenas {C,C7,F,Fm})
- Claudia Leitte - Bem Vindo Amor → `['C', 'C7', 'F', 'Fm']`, `True`
- Exaltasamba - Jogo de Sedução → `['C', 'C7', 'F', 'Fm']`, `True`
- Revelação - Jogo de Sedução → `['C', 'C7', 'F', 'Fm']`, `True`

## Resposta direta à pergunta
**Sim, com base no padrão observado no dataset:** para as músicas com tag de sequência famosa, o conjunto **único** de acordes da cifra é composto **apenas** pelos acordes daquela sequência. Ou seja, `set(acordes da cifra)` ⊆ `set(acordes da sequência)`. 

**Não é necessário que os acordes apareçam na ordem da chave concatenada.** A ordem não é verificada pelo código — o `main.py` não faz busca por subsequência nem por padrão de ordem; apenas verifica `str(id_seq) in musica.seqs_famosas` (`main.py:209`). Além disso, nos exemplos acima, muitas músicas com a mesma tag usam exatamente o mesmo conjunto único de acordes da sequência, independentemente da variação de ordem na cifra (como visto em seq 0 onde aparecem ciclos diferentes, mas o conjunto único permanece {A,Bm,D,G}).

**Observação importante:** isso é o padrão observado nas amostras inspecionadas do dataset, mas a atribuição da tag `SEQ_FAMOSA` é pré-computada (fora do runtime). O código atual não implementa essa regra — ele apenas usa the tags pré-existentes.

## Referências concretas
- `main.py:40-45` (mapa `sequencias`)
- `main.py:49-63` (carregamento CSV: divisão por `;` de `CIFRA` e `SEQ_FAMOSA`)
- `main.py:170-197,203-223` (roteamento `/similares` por sequência)
- `musica.py:17-18` (armazenamento `acordes = list(set(cifra))` e `seqs_famosas`)
- `data/top/dataset_final.csv` (coluna 8 `CIFRA`, coluna 7 `SEQ_FAMOSA`)
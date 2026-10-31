# Condições para sequência famosa no dataset_final.cs

## Resumo (3-6 frases)
Com base na verificação em todo o dataset, para **todas** as músicas marcadas com alguma das 6 sequências famosas (`SEQ_FAMOSA` com valores `0`-`5`), ambas as condições se verificam simultaneamente: (1) o conjunto único de acordes da cifra é composto **apenas** pelos acordes da sequência (`cset.issubset(scset)`) e (2) a sequência na ordem exata da chave mapeada aparece pelo menos uma vez de forma **contígua** na lista de acordes extraída da cifra. A contagem em todo o arquivo mostrou: `both: 514, cont: 514, only: 514`. Isso indica que, no dataset, as duas condições são coincidentes para essas músicas. Entretanto, **o código atual do `main.py` não implementa nenhuma dessas verificações** — ele apenas usa a tag pré-computada (`SEQ_FAMOSA` dividida por `;` em `main.py:63`, armazenada em `Musica.seqs_famosas` em `musica.py:18`, filtrada por `str(id_seq) in musica.seqs_famosas` em `main.py:209`).

## Mapa das sequências (conforme código)
`main.py:40-45`:
```python
sequencias = {'BmGDA' : 0,
        'CGAmF' : 1,
        'EmG' : 2,
        'CA7DmG7' : 3,
        'GmF' : 4,
        'CC7FFm' : 5}
```

## Verificação realizada
Para cada música com tag `0`-`5`:
- Extrai lista de acordes da cifra: `[x.strip() for x in row[8].split(';') if x.strip() != '']` (conforme processamento em `main.py:58-61`)
- Conjunto único da música `cset = set(c)`, conjunto da sequência `scset = set(sc)` (definido pelo mapa acima)
- `only_seq_chords = cset.issubset(scset)`
- `appears_contiguously = True` se existir algum índice j tal que `c[j:j+len(sc)] == sc` (busca por bloco exato contíguo na ordem da chave)

## Resultado
```text
both: 514 cont: 514 only: 514
```
Ou seja, **para todas as 514 entradas marcadas com sequências famosas no dataset, ambas as condições são verdadeiras simultaneamente**.

## Resposta direta à pergunta
**Sim, com base no dataset atual:** você pode considerar que, para as músicas com tag de sequência famosa, **ambas as condições** se aplicam:
1. A música é composta **apenas** pelos acordes da sequência (conjunto único da cifra é subconjunto do conjunto da sequência).
2. A sequência na ordem exata da chave mapeada aparece **pelo menos uma vez seguida (contígua)** na cifra.

Entretanto, é importante frisar: **isso é uma propriedade observada no dataset, não uma regra implementada no código**. O `main.py` não verifica ordem, não verifica continuidade, não verifica composição — apenas filtra por `str(id_seq) in musica.seqs_famosas` (`main.py:209`). A atribuição das tags foi feita em processo pré-computado (fora do runtime).

## Referências concretas
- `main.py:40-45` (mapa `sequencias`)
- `main.py:49-64` (carregamento CSV: `CIFRA` dividido por `;`, `SEQ_FAMOSA` dividido por `;`)
- `main.py:170-197,203-223` (roteamento `/similares` por sequência)
- `main.py:209` (`if str(id_seq) in musica.seqs_famosas:`)
- `musica.py:17-18` (`self.acordes = list(set(cifra))`, `self.seqs_famosas = seqs_famosas`)
- `data/top/dataset_final.csv` (colunas 7 `SEQ_FAMOSA`, 8 `CIFRA`)
- `research/composicao_cifras_por_sequencia_famosa.md`
- `research/sequencia_aparece_seguida.md`
- `research/mecanismo_sequencias_famosas.md`
- `check_seq_continuous.py` (script de verificação)
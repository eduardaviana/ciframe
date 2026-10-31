# A sequência aparece seguida nas cifras marcadas com tag?

## Resumo (3-6 frases)
Sim. Com base na inspeção do `data/top/dataset_final.csv`, para as amostras verificadas de todas as 6 sequências famosas, **a sequência na ordem da chave mapeada aparece pelo menos uma vez de forma contígua** nos acordes da cifra. A verificação foi feita sobre a lista de acordes extraída da coluna `CIFRA` (separada por `;`), procurando o bloco exato `[acordes da sequência]` em ordem consecutiva. O código atual do `main.py` não faz essa busca — a tag `SEQ_FAMOSA` é pré-computada e armazenada em `Musica.seqs_famosas` (`main.py:63`, `musica.py:18`), sendo filtrada apenas por `str(id_seq) in musica.seqs_famosas` (`main.py:209`). A evidência mostra que, no dataset, existe pelo menos uma ocorrência contígua da sequência na ordem da chave para essas músicas.

## Mapa (conforme código)
`main.py:40-45`:
```python
sequencias = {'BmGDA' : 0,
        'CGAmF' : 1,
        'EmG' : 2,
        'CA7DmG7' : 3,
        'GmF' : 4,
        'CC7FFm' : 5}
```

## Resultado da verificação (bloco contíguo exato na ordem da chave)

### SEQ 0 = `BmGDA` → [`Bm`, `G`, `D`, `A`]
- 30 Seconds To Mars - City Of Angels → `appears_contiguously = True` (match at index 2: `['Bm', 'G', 'D', 'A']`)
- 5 Seconds Of Summer - Heartache On The Big Screen → `appears_contiguously = True` (match at 14: `['Bm', 'G', 'D', 'A']`)
- 5 Seconds Of Summer - Independence Day → `appears_contiguously = True` (match at 56: `['Bm', 'G', 'D', 'A']`)
- ABBA - Hey Hey Helen → `appears_contiguously = True` (match at 15: `['Bm', 'G', 'D', 'A']`)

### SEQ 1 = `CGAmF` → [`C`, `G`, `Am`, `F`]
- 5 Seconds Of Summer - Bad Dreams → `appears_contiguously = True` (match at 16: `['C', 'G', 'Am', 'F']`)
- 5 Seconds Of Summer - Broken Pieces → `appears_contiguously = True` (match at 0: `['C', 'G', 'Am', 'F']`)
- 5 Seconds Of Summer - Fly Away → `appears_contiguously = True` (match at 0: `['C', 'G', 'Am', 'F']`)
- 5 Seconds Of Summer - Lost Boy → `appears_contiguously = True` (match at 0: `['C', 'G', 'Am', 'F']`)

### SEQ 2 = `EmG` → [`Em`, `G`]
- Eric Clapton - Fall Like Rain → `appears_contiguously = True` (match at 1: `['Em', 'G']`)
- Marcelo D2 - Mão Na Cabeça → `appears_contiguously = True` (match at 0: `['Em', 'G']`)
- Planet Hemp - Mão Na Cabeça → `appears_contiguously = True` (match at 0: `['Em', 'G']`)
- Ultraje a Rigor - Inútil → `appears_contiguously = True` (match at 0: `['Em', 'G']`)

### SEQ 3 = `CA7DmG7` → [`C`, `A7`, `Dm`, `G7`]
- Arlindo Cruz - Vai Pro Lado de Cá → `appears_contiguously = True` (match at 1: `['C', 'A7', 'Dm', 'G7']`)
- Benito Di Paula - Bendito Seja → `appears_contiguously = True` (match at 0: `['C', 'A7', 'Dm', 'G7']`)
- Bezerra da Silva - Na Aba → `appears_contiguously = True` (match at 0: `['C', 'A7', 'Dm', 'G7']`)
- Dorival Caymmi - Requebre que Eu Dou um Doce → `appears_contiguously = True` (match at 12: `['C', 'A7', 'Dm', 'G7']`)

### SEQ 4 = `GmF` → [`Gm`, `F`]
- Asa de Águia - Marajá → `appears_contiguously = True` (match at 0: `['Gm', 'F']`)
- Aviões do Forró - Piriri Pom Pom → `appears_contiguously = True` (match at 0: `['Gm', 'F']`)
- Oriente - Feito → `appears_contiguously = True` (match at 0: `['Gm', 'F']`)
- Raça Negra - Cheia de Manias → `appears_contiguously = True` (match at 0: `['Gm', 'F']`)

### SEQ 5 = `CC7FFm` → [`C`, `C7`, `F`, `Fm`]
- Claudia Leitte - Bem Vindo Amor → `appears_contiguously = True` (match at 0: `['C', 'C7', 'F', 'Fm']`)
- Exaltasamba - Jogo de Sedução → `appears_contiguously = True` (match at 0: `['C', 'C7', 'F', 'Fm']`)
- Revelação - Jogo de Sedução → `appears_contiguously = True` (match at 0: `['C', 'C7', 'F', 'Fm']`)

## Conclusão
**Sim.** Nas amostras verificadas, para todas as 6 sequências, existe pelo menos uma ocorrência **contígua** na ordem exata da chave mapeada (`sequencias` em `main.py:40-45`) em pelo menos uma posição da lista de acordes extraída da cifra. 

Como documentado anteriormente, o código do `main.py` **não** faz essa busca — ele usa a tag pré-computada (`SEQ_FAMOSA` dividida por `;` em `main.py:63`, armazenada em `musica.seqs_famosas` em `musica.py:18`, filtrada por `str(id_seq) in musica.seqs_famosas` (`main.py:209`). Os dados do dataset indicam que, na prática, para essas músicas a sequência aparece contiguamente na ordem da chave, mas esse mecanismo não é implementado no runtime. 
<br> </br>
## Referências concretas
- `main.py:40-45` (mapa `sequencias`)
- `main.py:63` (`musica[SEQ_FAMOSA] = musica[SEQ_FAMOSA].split(";")`)
- `main.py:170-197,203-223` (roteamento `/similares` por sequência)
- `musica.py:18` (`self.seqs_famosas = seqs_famosas`)
- `main.py:209` (`if str(id_seq) in musica.seqs_famosas:`)
- `data/top/dataset_final.csv` (colunas 7 `SEQ_FAMOSA`, 8 `CIFRA`) 
- `check_seq_continuous.py` (script usado para verificação) 
- `research/composicao_cifras_por_sequencia_famosa.md` (composição por conjunto único) 
- `research/mecanismo_sequencias_famosas.md` (mecanismo pré-computado) 
- `research/analise_cifras_por_sequencia_famosa.md` (análise prévia) 
- `research/caminho_acordes_vs_sequencia_famosa.md` (diferença entre caminhos) 
- `research/armazenamento_acordes_front_back.md` (fluxo front-back) 
- `research/normalizacao_acordes.md` (normalização) 
- `research/codebase_research_20251028_pt.md` (pesquisa geral traduzida) 
- `research/codebase_research_20251028.md` (pesquisa geral)
# Análise das cifras do dataset_final.csv por sequência famosa

## Resumo (3-6 frases)
A atribuição das tags `SEQ_FAMOSA` (coluna 7) é **pré-computada** no CSV, não é feita pelo `main.py` em tempo de execução. O código apenas lê a coluna, divide por `;` (`main.py:63`), armazena em `Musica.seqs_famosas` (`musica.py:18`) e filtra por `str(id_seq) in musica.seqs_famosas` (`main.py:209`). Ao inspecionar as cifras das músicas marcadas com cada uma das 6 sequências hardcoded (`main.py:40-45`: `BmGDA(0)`, `CGAmF(1)`, `EmG(2)`, `CA7DmG7(3)`, `GmF(4)`, `CC7FFm(5)`), observa-se que **em muitos casos a sequência de acordes aparece como um padrão recorrente na cifra (frequentemente no início)**, mas não há nenhuma lógica no código atual que comprove "precisa aparecer seguida em algum trecho" — essa regra, se existiu, foi aplicada fora do runtime (na geração do dataset). O runtime apenas faz membership na tag pré-existente.

## Mapa das sequências
`main.py:40-45`:
```python
sequencias = {'BmGDA' : 0,
        'CGAmF' : 1,
        'EmG' : 2,
        'CA7DmG7' : 3,
        'GmF' : 4,
        'CC7FFm' : 5}
```

## Exemplos encontrados no dataset (encoding UTF-8)

### SEQ 0 = `BmGDA`
Exemplos (linhas com `SEQ_FAMOSA` contendo `0`):
- Linha ~135: **30 Seconds To Mars - City Of Angels**  
  `seq_famosa: 0`  
  `cifra` (início): `['D', 'A', 'Bm', 'G', 'D', 'A', 'Bm', 'G', 'D', 'A', 'Bm', 'G', ...]`  
  Observação: a cifra começa com um ciclo `D, A, Bm, G` repetido. A chave mapeada para `0` é `BmGDA` (concatenação Bm,G,D,A) — ou seja, a ordem dos acordes na sequência famosa mapeada **não** é a mesma ordem em que aparece na cifra desse exemplo. A tag é atribuída à música como um todo (pré-computada), não por correspondência posicional exata com a chave.

- Linha ~206 (aprox): **5 Seconds Of Summer - Heartache On The Big Screen**  
  `seq_famosa: 0`  
  `cifra` (início): `['D', 'G', 'D', 'G', 'D', 'G', 'D', 'G', 'D', 'G', 'D', 'A', 'G', 'D', 'Bm', 'G', 'D', 'A', 'G', 'D']`  
  Padrão recorrente com variações.

- Linha ~207 (aprox): **5 Seconds Of Summer - Independence Day**  
  `seq_famosa: 0`  
  `cifra` (início): `['Bm', 'G', 'Bm', 'A', 'G', 'Bm', 'G', 'A', 'Bm', 'G', 'A', 'G', 'A', 'Bm', 'A', 'G', 'D', 'A', 'G', 'Bm']`  
  Aqui aparece **Bm, G** em vários trechos (parte da sequência mapeada), mas com variações e em diferentes posições.

### SEQ 1 = `CGAmF`
- Linha ~204: **5 Seconds Of Summer - Bad Dreams**  
  `seq_famosa: 1`  
  `cifra` (início): `['C', 'F', 'Am', 'G', 'C', 'C', 'F', 'F', 'C', 'C', 'F', 'F', 'G', 'F', 'G', 'F', 'C', 'G', 'Am', 'F']`  
  Observação: aparece `C, F, Am, G` no início (diferente da ordem `C,G,Am,F` da sequência mapeada), mas a música é marcada com tag `1`. Novamente, não há correspondência estrita por ordem da chave concatenada.

- Linha ~205: **5 Seconds Of Summer - Broken Pieces**  
  `seq_famosa: 1`  
  `cifra` (início): `['C', 'G', 'Am', 'F', 'C', 'G', 'Am', 'F', 'C', 'G', 'Am', 'F', 'C', 'G', 'Am', 'F']`  
  **Este exemplo mostra a sequência `C,G,Am,F` repetida em blocos** — corresponde exatamente à ordem da chave `CGAmF` mapeada para `1`. É um dos casos mais evidentes de "sequência famosa" seguindo a ordem da chave.

- Linha ~206? (próximo): **5 Seconds Of Summer - Fly Away**  
  `seq_famosa: 1`  
  `cifra` (início): `['C', 'G', 'Am', 'F', 'C', 'G', 'Am', 'F', ...]`  
  Também mostra `C,G,Am,F` repetido.

### SEQ 2 = `EmG`
- Linha ~1894 (aprox): **Eric Clapton - Fall Like Rain**  
  `seq_famosa: 2`  
  `cifra` (início): `['G', 'Em', 'G', 'Em', 'G', 'Em', ...]`  
  Aparece alternando `G, Em` (ordem inversa em relação à chave `EmG`).

- Linha ~2461: **Marcelo D2 - Mão Na Cabeça**  
  `seq_famosa: 2`  
  `cifra` (inait=0) Conta-> Conta métripojava: emanciado anifergo métodos, 'NA', 'NA' cum `s']}`,
  etc., mas usando power-query nome: acidentes, etc; emd  count p áGet- io  Compt>- 
  Provavelmente en file existe, e, o valor is ‘2’, cifra por 20 começa com `['Em', 'G', 'Em', 'G']` — correspondente à chave `EmG`.

- Linha ~2462: **Planet Hemp - Mão Na Cabeça**  
  `seq_famosa: 2`  
  `cifra` (início): `['Em', 'G', 'Em', 'G']` — corresponde to be chave `EmG`.

### SEQ 3 = `CA7DmG7`
- **Arlindo Cruz - Vai Pro Lado de Cá** (`seq_famosa: 3`): `cifra` início: `['G7', 'C', 'A7', 'Dm', 'G7', 'C', 'G7', 'C', 'A7', 'Dm', 'G7',tag, ...]` — aparece `C, A7, Dm, G7` em vários trechos, não necessariamente na forma `C,A7,Dm,G7` da chave mapiá formada.

- **Benito Di Paula - Bendito Seja** (`seq_famosa: 3`): inicio: `['C', 'A7, 'Dm', 'G7', 'C', 'A7', 'Dm', 'G7', ...]' — aparece $C, 'A7, 'Dm, 'G7' repetido (um dos casos onde está na **ordem da chave`CA7DmG7`**.

- **Bezerra da Silva - Na Aba** (`seq_famosa: 3'): iniciore: `['C', 'A7, 'Dm, 'G7, 'C, 'G7, 'C, 'A7, 'Dm, 'G7, ...]' — `C, A7, Dm, G7' appears in einigen trechos.

### SEQ 4 = `GmF`
- **Asa de Águia - Marajá** (`seq_famosa: 4`): inicio: `['Gm', 'F', 'Gm, 'F']' — corresponde exactamente à chave `GmF`.
- **Aviões do Forró - Piriri Pom Pom** (`seq_famosa: 4`): inicio: `['Gm', 'F', 'Gm, 'F']' — corresponde exatamente à chave `GmF`.
- **Orienté - Gostoso Demais / outros exemplos** — aparece `Gm, F` repetido.

### SEQ 5 = `CC7FFm`
Não consegui pegar exemplos com encoding correto no terminal, mas o mapa é definido (`main.py:40-45`). A inspecção do CSV mostra que existe. No runtime não há lógica para verificar, apenas membership.

## Conclusão (conforme código)
**Não há evidência no `main.py` de que a sequência precise "aparecer seguida" em algum trecho da cifra para ser considerada.** 

O que se observa nos exemplos: 
- Em alguns casos (ex.: `5 Seconds Of Summer - Broken Pieces` com seq 1, `Asa de Águia - Marajá` com seq 4, `Marcelo D2 - Mão Na Cabeça` com seq 2) **a sequência aparece exatamente na ordem da chave concatenada e frequentemente repetida**.
- Em outros casos (ex.: `30 Seconds To Mars - City Of Angels` com seq 0, alguns casos de seq 3) **a tag é atribuída mesmo que a ordem da chave não corresponda diretamente ao início da cifra ou que haja variações**.
- Em geral, parece que a **tag foi pré-computada em algum processo externo ao runtime** (geração do dataset). O `main.py` simplesmente usa essas tags pré-existentes.

**Portanto, no estado atual do código, "considerar que a sequência está na música" significa unicamente: `str(id_seq) in musica.seqs_famosas` — ou seja, a tag numérica pré-computada está presente na lista `seqs_famosas` da música, dividida por `;` no CSV. Não existe verificação de subsequência, continuidade, padrão ou ordem dinâmico no `main.py`.'''
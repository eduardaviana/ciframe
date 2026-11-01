# Proposta — Sequências de Acordes Customizadas

## Abordagem escolhida

### Algoritmo de matching

A abordagem escolhida foi calcular o matching em tempo real a cada busca. A regra que define se uma música é compatível com uma sequência cadastrada é:

Uma música é compatível com uma sequência (lista ordenada de acordes) se somente se as duas condições forem verdadeiras:

1. A sequencia aparece como subsequência, continua e na mesma ordem, em música.cifra pelo menos uma vez.
2. O conjunto de acordes da música é subconjunto do conjunto de acordes de sequencia.

O algoritmo recebe como entrada a lista de acordes da sequência, percorre as músicas carregadas em memória a partir do CSV e retorna as que satisfazem as duas condições. 

### Banco de dados

O banco de dados escolhido foi o SQLite, utilizando sqlite3 da biblioteca padrão do Python. Pois, além de ser compatível com o que a adr-0001 pede, entre as opções pesquisadas, ele é o que exige menos mudanças entre os arquivos do projeto, como por exemplo não precisar adicionar linhas no requirements.txt, além de ser simples para controle de escritas concorrentes. 

### Esquema de dados (alto nível)

Uma tabela `sequencias`:

- `id`: INTEGER -> identificador numérico, chave primária
- `sequencia`: TEXT UNIQUE ->  acordes da sequência concatenados e únicos 
- `acordes`: TEXT -> lista dos acordes presentes da sequencia separados por ;

### API

Novos:
- `GET /sequencias`: devolve o catálogo completo com as sequencias originais e cadastradas possuindo id, sequencia e acordes.

    Entrada: sem nenhum parametro 

    Saida: [{"id": 0, "sequencia": "BmGDA","acordes": "Bm;G;D;A"}, ...]
- `POST /sequencias`: cadastro anônimo, com tratamento de erro para sequência já cadastrada e tamanho invalido de acordes (len(acordes) < 2).

    Entrada: `{"sequencia": ["Bm","G","D","A"]}`.

    Saída: `{"id": 0, "sequencia": "BmGDA", "acordes": "Bm;G;D;A"}`

Alterado:
- `GET /similares?sequencia=...`: muda internamente para passar a buscar a sequência no catálogo do banco, em vez de filtrar pela tag seqs_famosas do CSV. Entrada e saida permanece a mesma:

    Entrada: `GET /similares?sequencia=Bm,G,D,A&generos=MPB`

    Saida: lista de musicas correspondentes. 


### Frontend

- Remover as sequências fixas presentes no código e passar a carregar o catálogo com `GET /sequencias` ao iniciar o controller. 
- Adicionar um espaço de cadastro com seleção de acordes por botões, reaproveitando o padrão da página #/poracordes. Ao enviar, chama `POST /sequencias` recarregando o catálogo ou, em caso de erro, mostra mensagem vinda do POST.
- A busca continua igual, ao clicar em qualquer sequência  chama `GET /similares?sequencia=...` com o filtro opcional por gênero e a ordenação por popularidade.

## Alternativas consideradas e descartadas

Ao ler as propostas, a que pensei em considerar foi a utilização do DuckDB + cálculo do matching feito como pré-cálculo com o objetivo da busca ficar mais rápida. Entretanto, para fazer esse cálculo e otimizar a busca seria preciso criar uma nova tabela no banco guardando as músicas de cada sequência, o que quebra um dos requisitos, que é continuar lendo as músicas do CSV em memória. Logo, descartei pois a proposta de utilizar SQLite cumpria melhor com os requisitos. 

## Escopo explícito

**Dentro do escopo:**

- Cadastro anônimo de sequências por botões de acordes, com validação de tamanho (no minimo 2) e duplicatas.
- Persistência do catálogo com SQLite, com as 6 sequencias originais carregadas na inicialização.
- Criação das rotas `GET /sequencias`, `POST /sequencias` e alteração de `GET /similares` para passar a buscar a sequência no banco e aplicar a regra de matching em tempo real.
- #/porsequencia exibindo o catálogo vindo do backend, com cadastro e busca por qualquer sequência.
- Algoritmo matching em tempo real aplicando a regra das duas condições.


**Fora do escopo (e por quê):**

- Login de usuario: O catálogo foi definido como aberto e anônimo.
- Digitação livre de acordes e normalização da entrada: o cadastro por botões dispensa isso e reduz erros.
- Migrar músicas e gêneros para o banco: O catálogo de musica foi definido para continuar sendo lido do arquivo CSV em memória.

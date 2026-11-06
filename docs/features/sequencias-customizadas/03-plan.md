# Plano — Sequências de Acordes Customizadas

## Passos

1. [ ] **Preparação do banco de dados (SQLite)**
   - [ ] Criar lógica para inicialização do banco SQLite em `main.py` (ou módulo dedicado). Usar `sqlite3` da biblioteca padrão.
   - [ ] Criar tabela `sequencias` com esquema: `id INTEGER PRIMARY KEY`, `sequencia TEXT UNIQUE`, `acordes TEXT` (acordes separados por `;`).
   - [ ] Fazer seed das 6 sequências originais na inicialização, mapeando as entradas hardcoded em `main.py:40-45` para o formato do banco.
   - [ ] Garantir criação do diretório `data/db/` e salvar o arquivo `.db` em `data/db/sequencias.db` (caminho configurável), tratando persistência via volume (documentação).
   - [ ] Adicionar `data/db/` (ou `*.db`) ao `.gitignore`.

2. [ ] **Implementação do algoritmo de matching em tempo real**
   - [ ] Implementar função para verificar se uma música é compatível com uma sequência, aplicando **exatamente** as duas condições validadas:
     1. A sequência ordenada aparece pelo menos uma vez na lista ordenada de cifras da música (`musica.cifra`, gerada por `limpa_cifra()` em `main.py:11-23`).
     2. Todos os acordes distintos da música (`musica.acordes`, `musica.py:17`) formam um subconjunto do conjunto de acordes da sequência (`set(musica.acordes) ⊆ set(sequencia)`).
   - [ ] Validar contra as 6 sequências originais comparando com os resultados esperados via `SEQ_FAMOSA` (baseado em `research/algoritmo/test_hipotese_sequencias_famosas.py` com 0 divergências).
   - [ ] Garantir que o matching não adiciona `diferenca`/`intersecao` ao objeto retornado para o caminho por sequência (mantendo formato atual `main.py:210-221`).

3. [ ] **Implementação das rotas da API**
   - [ ] Criar `GET /sequencias`: retornar catálogo completo (originais + cadastradas), ordenado por `id`. Saída: `json.dumps([{"id": ..., "sequencia": "BmGDA", "acordes": "Bm;G;D;A"}, ...])`. Sem parâmetros.
   - [ ] Criar `POST /sequencias`: cadastro anônimo. Entrada: `{"sequencia": ["Bm","G","D","A"]}`.
     - Validações: corpo deve ser um objeto JSON com a chave `sequencia`; `sequencia` deve ser uma lista com `len(acordes) >= 2`; não permitir duplicatas (mesma chave concatenada já existente). Não aplicar trim nem normalização aos acordes: usar os itens como vieram (itens não-string são rejeitados para evitar erro de concatenação).
     - Sucesso: HTTP 200 com `json.dumps({"id": ..., "sequencia": "BmGDA", "acordes": "Bm;G;D;A"})`.
     - Erros: HTTP 400 com `json.dumps({"erro": "..."})` para payload inválido ou `len(acordes) < 2`; HTTP 409 com `json.dumps({"erro": "..."})` para sequência duplicada.
     - Manter padrão de retorno com `json.dumps(...)` (não `jsonify`).
   - [ ] Alterar `GET /similares`: ao receber parâmetro `sequencia`, buscar a sequência no catálogo do banco SQLite (ao invés de filtrar por `seqs_famosas` do CSV). Aplicar o matcher em tempo real com as duas condições. Manter entrada/saída no formato atual (`?sequencia=Bm,G,D,A&generos=...` opcional), paginação e ordenação existentes, e continuar retornando `json.dumps(...)`.

4. [ ] **Atualização do frontend (`#/porsequencia`)**
   - [ ] Remover as sequências hardcoded `sequencia1..sequencia4` de `static/assets/js/controllers/sequencia.js:2-37`.
   - [ ] Carregar o catálogo via `GET /sequencias` no início do `SequenciaController` (chamada direta; AngularJS 1.4.9 não tem `$onInit`) e popular `vm.sequenciasFamosas` com os itens do backend convertidos para o formato dos hexágonos: `acordes.split(';')` -> `[{acorde, cor}]`, usando `#2E1C74` para todas as sequências.
   - [ ] Exibir o catálogo completo (6 originais + novas) só com hexágonos, sem nome/rótulo, mantendo o layout atual do painel esquerdo. Novas sequências aparecem ao final porque `GET /sequencias` ordena por `id`.
   - [ ] Adicionar o botão "Cadastrar sequência" acima do catálogo, no painel esquerdo, abrindo um modal suspenso (`$uibModal` com template inline em `sequencia.html`, sem criar arquivo novo).
   - [ ] No modal, montar a sequência com a mesma grade de hexágonos de `#/poracordes`:
     - cada clique em um hexágono **acrescenta** o acorde ao fim da lista, mesmo que ele já tenha sido escolhido (repetição permitida);
     - a sequência montada aparece em ordem em uma faixa própria; clicar em um acorde dessa faixa remove **aquela ocorrência**;
     - não haverá reordenação por drag-and-drop nem setas; para mudar a ordem, o usuário remove e adiciona de novo;
     - exibir apenas a quantidade selecionada, sem limite máximo.
   - [ ] Validar no frontend apenas o mínimo de 2 acordes:
     - menos de 2: manter o botão "Cadastrar" desabilitado e exibir "Escolha pelo menos 2 acordes.";
     - não impor limite máximo de acordes.
   - [ ] Enviar `POST /sequencias` com `{"sequencia": [acordes na ordem]}`:
     - sucesso (200): limpar a seleção, fechar o modal, recarregar o catálogo com `GET /sequencias` e mostrar "Sequência cadastrada com sucesso." em um aviso suspenso sobre o painel esquerdo, que desaparece automaticamente após alguns segundos;
     - erro 400: mostrar inline no modal a mensagem `data.erro` vinda do backend;
     - erro 409: mostrar inline no modal a mensagem `data.erro` ("sequência já cadastrada");
     - erro de rede/servidor: mostrar inline no modal "Não foi possível cadastrar a sequência. Tente novamente.".
   - [ ] Se `GET /sequencias` falhar ao carregar o catálogo, mostrar "Não foi possível carregar o catálogo." no painel esquerdo.
   - [ ] Garantir que ao clicar em qualquer sequência (antiga ou nova) a busca chame `GET /similares?sequencia=...` com a lista de acordes separada por vírgulas e filtro opcional por gênero, mantendo a ordenação por popularidade e o comportamento existente do template (`static/templates/sequencia.html`).
   - [ ] Garantir que o catálogo exibido reflete o que vem do backend (resolvendo o descompasso entre 4 sequências no frontend e 6 no backend).

5. [ ] **Limpeza e integração**
   - [ ] Remover ou desativar lógica dependente das tags `SEQ_FAMOSA` para o caminho de busca por sequência customizável, mantendo compatibilidade com as 6 originais via catálogo do banco.
   - [ ] Garantir que `musicas` e `generos` continuem sendo carregados do CSV em memória como hoje (`main.py:49-98`) - não migrar para o banco.
   - [ ] Verificar que todos os endpoints continuam retornando `json.dumps(...)`.

## Arquivos afetados

| Arquivo | Mudança |
|---|---|
| `main.py` | Inicialização do SQLite, seed das 6 sequências originais, implementação do matcher em tempo real com as duas condições, novas rotas `GET /sequencias` e `POST /sequencias`, alteração de `GET /similares` para buscar no banco e aplicar matcher. |
| `musica.py` | Sem alterações obrigatórias (manter `musica.cifra` e `musica.acordes` conforme estrutura atual). |
| `static/assets/js/controllers/sequencia.js` | Remover sequências hardcoded, carregar catálogo via `GET /sequencias`, adicionar lógica de cadastro (`POST /sequencias`), manter fluxo de busca. |
| `static/templates/sequencia.html` | Adicionar interface para cadastro de nova sequência por botões de acordes (reaproveitando padrão de `#/poracordes`), exibir catálogo vindo do backend. |
| `(novo) data/db/sequencias.db` ou diretório de banco | Arquivo SQLite a ser criado em `data/db/` na inicialização. Deve ficar em local montável por volume (documentar). |

## Riscos e mitigação

| Risco | Como perceber | Mitigação |
|---|---|---|
| Quebra de regressão nas 6 sequências originais | Resultados diferentes dos esperados via `SEQ_FAMOSA`. | Validar matcher com o script/critério de `research/algoritmo/test_hipotese_sequencias_famosas.py` (0 divergências). Testar as 6 sequências hardcoded contra o novo fluxo. |
| Duplicatas/entrada inválida no cadastro | `POST /sequencias` permite sequência duplicada ou com < 2 acordes. | Aplicar validações: `len(chords) >= 2`, normalizar chave para unicidade (`sequencia` concatenado), retornar erro apropriado em caso de duplicata. |
| Persistência entre recriação do container | Dados customizados somem após `docker rm`/recriação. | Documentar que é necessário montar volume para o diretório do banco (conforme ADR 0002). Código deve criar diretório se não existir. |
| Desvio da regra de matching | Usar apenas "presença na cifra" ou lógica parecida com `get_similares`. | Seguir rigorosamente as duas condições validadas. Não adicionar `diferenca`/`intersecao` ao resultado do caminho por sequência. |
| Incompatibilidade com contrato da API | Usar `jsonify` ao invés de `json.dumps`. | Garantir todos os novos/alterados endpoints retornam `json.dumps(...)` conforme exigido. |

## Definição de pronto

- [ ] **Catálogo persistido:** Sequências cadastradas via `POST /sequencias` permanecem no catálogo após reiniciar o container (com volume montado). As 6 originais são carregadas na inicialização.
- [ ] **Cadastro funcional:** É possível cadastrar uma nova sequência ordenada por botões (anônimo), com validação de tamanho >= 2 e tratamento de duplicatas.
- [ ] **Busca funcional:** Qualquer sequência cadastrada (originais + novas) pode ser usada em `GET /similares?sequencia=...`, retornando músicas que atendem às duas condições do matching.
- [ ] **Regressão OK:** As 6 sequências originais continuam produzindo **exatamente** os mesmos resultados que produziam via `SEQ_FAMOSA` (validado contra `research/algoritmo/test_hipotese_sequencias_famosas.py`).
- [ ] **Frontend atualizado:** `#/porsequencia` exibe catálogo real vindo do backend (sem hardcode de `sequencia1..sequencia4`), permite cadastro e busca por qualquer sequência.
- [ ] **Restrições respeitadas:** Músicas/gêneros continuam do CSV em memória; uso de SQLite (stdlib); endpoints com `json.dumps(...)`; container único/local-only mantido.
- [ ] **Documentação:** ADR 0002 existente e coerente com a implementação; alterações necessárias documentadas (volume para persistência).
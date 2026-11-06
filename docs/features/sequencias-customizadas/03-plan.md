# Plano — Sequências de Acordes Customizadas

## Passos

1. [x] **Preparação do banco de dados (SQLite)**
   - [x] Criar lógica para inicialização do banco SQLite em `main.py` (ou módulo dedicado). Usar `sqlite3` da biblioteca padrão.
   - [x] Criar tabela `sequencias` com esquema: `id INTEGER PRIMARY KEY`, `sequencia TEXT UNIQUE`, `acordes TEXT` (acordes separados por `;`).
   - [x] Fazer seed das 6 sequências originais na inicialização, mapeando as entradas hardcoded em `main.py:40-45` para o formato do banco.
   - [x] Garantir criação do diretório `data/db/` e salvar o arquivo `.db` em `data/db/sequencias.db` (caminho configurável), tratando persistência via volume (documentação).
   - [x] Adicionar `data/db/` (ou `*.db`) ao `.gitignore`.

2. [x] **Implementação do algoritmo de matching em tempo real**
   - [x] Implementar função para verificar se uma música é compatível com uma sequência, aplicando **exatamente** as duas condições validadas:
     1. A sequência ordenada aparece pelo menos uma vez na lista ordenada de cifras da música (`musica.cifra`, gerada por `limpa_cifra()` em `main.py:11-23`).
     2. Todos os acordes distintos da música (`musica.acordes`, `musica.py:17`) formam um subconjunto do conjunto de acordes da sequência (`set(musica.acordes) ⊆ set(sequencia)`).
   - [x] Validar contra as 6 sequências originais comparando com os resultados esperados via `SEQ_FAMOSA` (baseado em `research/algoritmo/test_hipotese_sequencias_famosas.py` com 0 divergências).
   - [x] Garantir que o matching não adiciona `diferenca`/`intersecao` ao objeto retornado para o caminho por sequência (mantendo formato atual `main.py:210-221`).

3. [x] **Implementação das rotas da API**
   - [x] Criar `GET /sequencias`: retornar catálogo completo (originais + cadastradas), ordenado por `id`. Saída: `json.dumps([{"id": ..., "sequencia": "BmGDA", "acordes": "Bm;G;D;A"}, ...])`. Sem parâmetros.
   - [x] Criar `POST /sequencias`: cadastro anônimo. Entrada: `{"sequencia": ["Bm","G","D","A"]}`.
     - Validações: corpo deve ser um objeto JSON com a chave `sequencia`; `sequencia` deve ser uma lista com `len(acordes) >= 2`; não permitir duplicatas (mesma chave concatenada já existente). Não aplicar trim nem normalização aos acordes: usar os itens como vieram (itens não-string são rejeitados para evitar erro de concatenação).
     - Sucesso: HTTP 200 com `json.dumps({"id": ..., "sequencia": "BmGDA", "acordes": "Bm;G;D;A"})`.
     - Erros: HTTP 400 com `json.dumps({"erro": "..."})` para payload inválido ou `len(acordes) < 2`; HTTP 409 com `json.dumps({"erro": "..."})` para sequência duplicada.
     - Manter padrão de retorno com `json.dumps(...)` (não `jsonify`).
   - [x] Alterar `GET /similares`: ao receber parâmetro `sequencia`, buscar a sequência no catálogo do banco SQLite (ao invés de filtrar por `seqs_famosas` do CSV). Aplicar o matcher em tempo real com as duas condições. Manter entrada/saída no formato atual (`?sequencia=Bm,G,D,A&generos=...` opcional), paginação e ordenação existentes, e continuar retornando `json.dumps(...)`.

4. [x] **Atualização do frontend (`#/porsequencia`)**
   - [x] Remover as sequências hardcoded `sequencia1..sequencia4` de `static/assets/js/controllers/sequencia.js:2-37`.
   - [x] Carregar o catálogo via `GET /sequencias` no início do `SequenciaController` (chamada direta; AngularJS 1.4.9 não tem `$onInit`) e popular `vm.sequenciasFamosas` com os itens do backend convertidos para o formato dos hexágonos: `acordes.split(';')` -> `[{acorde, cor}]`, usando `#2E1C74` para todas as sequências.
   - [x] Exibir o catálogo completo (6 originais + novas) só com hexágonos, sem nome/rótulo, mantendo o layout atual do painel esquerdo. Novas sequências aparecem ao final porque `GET /sequencias` ordena por `id`.
   - [x] Adicionar o botão "Cadastrar sequência" acima do catálogo, no painel esquerdo, abrindo um modal suspenso (`$uibModal` com template inline em `sequencia.html`, sem criar arquivo novo).
   - [x] No modal, montar a sequência com a mesma grade de hexágonos de `#/poracordes`:
     - cada clique em um hexágono **acrescenta** o acorde ao fim da lista, mesmo que ele já tenha sido escolhido (repetição permitida);
     - a sequência montada aparece em ordem em uma faixa própria; clicar em um acorde dessa faixa remove **aquela ocorrência**;
     - não haverá reordenação por drag-and-drop nem setas; para mudar a ordem, o usuário remove e adiciona de novo;
     - exibir apenas a quantidade selecionada, sem limite máximo.
   - [x] Validar no frontend apenas o mínimo de 2 acordes:
     - menos de 2: manter o botão "Cadastrar" desabilitado e exibir "Escolha pelo menos 2 acordes.";
     - não impor limite máximo de acordes.
   - [x] Enviar `POST /sequencias` com `{"sequencia": [acordes na ordem]}`:
     - sucesso (200): limpar a seleção, fechar o modal, recarregar o catálogo com `GET /sequencias` e mostrar "Sequência cadastrada com sucesso." em um aviso suspenso sobre o painel esquerdo, que desaparece automaticamente após alguns segundos;
     - erro 400: mostrar inline no modal a mensagem `data.erro` vinda do backend;
     - erro 409: mostrar inline no modal a mensagem `data.erro` ("sequência já cadastrada");
     - erro de rede/servidor: mostrar inline no modal "Não foi possível cadastrar a sequência. Tente novamente.".
   - [x] Se `GET /sequencias` falhar ao carregar o catálogo, mostrar "Não foi possível carregar o catálogo." no painel esquerdo.
   - [x] Garantir que ao clicar em qualquer sequência (antiga ou nova) a busca chame `GET /similares?sequencia=...` com a lista de acordes separada por vírgulas e filtro opcional por gênero, mantendo a ordenação por popularidade e o comportamento existente do template (`static/templates/sequencia.html`).
   - [x] Garantir que o catálogo exibido reflete o que vem do backend (resolvendo o descompasso entre 4 sequências no frontend e 6 no backend).

5. [x] **Limpeza e integração**
   - [x] Remover ou desativar lógica dependente das tags `SEQ_FAMOSA` para o caminho de busca por sequência customizável, mantendo compatibilidade com as 6 originais via catálogo do banco.
   - [x] Garantir que `musicas` e `generos` continuem sendo carregados do CSV em memória como hoje (`main.py:49-98`) - não migrar para o banco.
   - [x] Verificar que todos os endpoints continuam retornando `json.dumps(...)`.

### Testes

#### Automatizados por passo

- **Passo 1 — banco e seed:** `tests/test_passo1_exec_main.py` e `tests/test_passo1_docker_persistence.py`
  - `tests/test_passo1_exec_main.py` usa `SEQUENCIAS_DB_PATH` apontando para um banco temporário e não toca em `data/db/sequencias.db`; verifica criação do diretório/arquivo, tabela `sequencias`, restrição `UNIQUE`, seed das 6 originais, ausência de duplicatas e persistência de uma sequência customizada após nova inicialização.
  - `tests/test_passo1_docker_persistence.py` constrói a imagem, cadastra uma sequência em um volume nomeado, remove/recria o container com o mesmo volume e confirma a persistência; depois sobe sem volume e confirma que só as 6 originais existem. Se o Docker não estiver disponível, o teste é ignorado com `SKIP`.
- **Passo 2 — matcher:** `tests/test_passo2_matcher.py`
  - Regressão contra `SEQ_FAMOSA` para as 6 originais, exigindo 0 divergências.
  - Casos sintéticos de ordem, contiguidade, subconjunto de acordes, sequência vazia, cifra vazia, sequência maior que a cifra e acordes repetidos.
- **Passo 3 — rotas:** `tests/test_passo3_routes.py`
  - `GET /sequencias`, `POST /sequencias` e `/similares?sequencia=...`, com banco temporário isolado.
  - Status 200, 400 e 409; mensagens de erro exatas; acorde não-string; preservação de espaços/sem normalização; ausência de limite máximo; duplicata; filtro opcional `generos`; paginação; ordenação por popularidade; ausência de `diferenca`/`intersecao` no caminho por sequência.
- **Passo 4 — frontend:** `tests/test_passo4_frontend.md` e `tests/sequencia.spec.js`
  - `tests/sequencia.spec.js` (Playwright) cobre catálogo vindo de `GET /sequencias`, abertura do modal, seleção de acordes, POST, toast, recarga do catálogo, busca pela sequência nova, duplicata, erro de rede, erro de catálogo e ausência de rolagem horizontal em 375px.
  - `tests/test_passo4_frontend.md` permanece como checklist manual para detalhes visuais e responsividade que não valem um teste E2E.
- **Passo 5 — integração:** `tests/test_passo5_integration.py`
  - Usa banco temporário isolado; busca funciona com `seqs_famosas` desativado.
  - Músicas/gêneros continuam vindos do CSV em memória.
  - Endpoints de API continuam retornando `json.dumps` com `Content-Type: text/html`.

#### Contrato da API

- `GET /sequencias` → 200, lista ordenada por `id`.
- `POST /sequencias` com 2 ou mais acordes → 200.
- `POST /sequencias` com menos de 2 acordes → 400.
- `POST /sequencias` duplicada → 409.
- `GET /similares?sequencia=...` → 200 e lista de músicas.
- `GET /similares?sequencia=INEXISTENTE` → `[]`.
- Todas as respostas de API devem ser JSON válido e continuar com `Content-Type: text/html` (padrão `json.dumps`).

#### Persistência

- Cobertura automatizada: `py tests/test_passo1_docker_persistence.py` (volume nomeado, remoção/recriação e execução sem volume).
- Equivalente manual: subir com volume `docker run -p 8080:8080 -v "${PWD}/data/db:/app/data/db" ciframe`, cadastrar uma sequência, reiniciar o container e confirmar que ela continua em `GET /sequencias`.
- Recriar o container sem volume e confirmar que apenas as 6 originais são recriadas.

#### Regressão final

Comando único, a partir da raiz do repositório:

```powershell
npm.cmd install
npm.cmd test
```

`npm.cmd test` executa os 5 scripts Python e o Playwright. Os comandos
individuais continuam disponíveis:

```powershell
py tests/test_passo1_exec_main.py
py tests/test_passo1_docker_persistence.py
py tests/test_passo2_matcher.py
py tests/test_passo3_routes.py
py tests/test_passo5_integration.py
npm.cmd run test:frontend
```

O teste de browser usa o Microsoft Edge instalado por padrão (`PW_CHANNEL` pode
ser definido para outro canal do Playwright). O checklist manual do Passo 4
continua disponível para detalhes visuais em 375px, 768px e 1280px.

## Arquivos afetados

| Arquivo | Mudança |
|---|---|
| `main.py` | Inicialização do SQLite (com caminho configurável por `SEQUENCIAS_DB_PATH`), seed das 6 sequências originais, implementação do matcher em tempo real com as duas condições, novas rotas `GET /sequencias` e `POST /sequencias`, alteração de `GET /similares` para buscar no banco e aplicar matcher. |
| `musica.py` | Sem alterações obrigatórias (manter `musica.cifra` e `musica.acordes` conforme estrutura atual). |
| `static/assets/js/controllers/sequencia.js` | Remover sequências hardcoded, carregar catálogo via `GET /sequencias`, adicionar lógica de cadastro (`POST /sequencias`), manter fluxo de busca. |
| `static/templates/sequencia.html` | Adicionar interface para cadastro de nova sequência por botões de acordes (reaproveitando padrão de `#/poracordes`), exibir catálogo vindo do backend. |
| `(novo) data/db/sequencias.db` ou diretório de banco | Arquivo SQLite criado automaticamente. O caminho padrão é `data/db/sequencias.db` e pode ser alterado por `SEQUENCIAS_DB_PATH`; deve ficar em local montável por volume. |
| `README.md` | Documentar o SQLite, a variável `SEQUENCIAS_DB_PATH`, o comando Docker com volume e o comportamento sem volume. |
| `tests/test_passo1_exec_main.py`, `tests/test_passo2_matcher.py`, `tests/test_passo3_routes.py`, `tests/test_passo5_integration.py` | Testes automatizados por passo, com banco temporário. |
| `tests/test_passo1_docker_persistence.py` | Teste automatizado de persistência com volume Docker. |
| `tests/test_passo4_frontend.md` | Checklist manual versionado do frontend. |
| `tests/sequencia.spec.js`, `playwright.config.js`, `package.json`, `package-lock.json` | Teste de browser do Passo 4 com Playwright. |
| `tests/run-all.js` | Executa todos os testes automatizados com um único comando (`npm.cmd test`). |
| `.gitignore`, `.dockerignore` | Exclusão de artefatos de teste e `node_modules` do repositório e da imagem Docker. |

## Riscos e mitigação

| Risco | Como perceber | Mitigação |
|---|---|---|
| Quebra de regressão nas 6 sequências originais | Resultados diferentes dos esperados via `SEQ_FAMOSA`. | Validar matcher com o script/critério de `research/algoritmo/test_hipotese_sequencias_famosas.py` (0 divergências). Testar as 6 sequências hardcoded contra o novo fluxo. |
| Duplicatas/entrada inválida no cadastro | `POST /sequencias` permite sequência duplicada ou com < 2 acordes. | Aplicar validações: `len(chords) >= 2`, normalizar chave para unicidade (`sequencia` concatenado), retornar erro apropriado em caso de duplicata. |
| Persistência entre recriação do container | Dados customizados somem após `docker rm`/recriação. | Documentado no README que é necessário montar volume para o diretório do banco (conforme ADR 0002). O código cria o diretório se não existir e aceita `SEQUENCIAS_DB_PATH`. |
| Desvio da regra de matching | Usar apenas "presença na cifra" ou lógica parecida com `get_similares`. | Seguir rigorosamente as duas condições validadas. Não adicionar `diferenca`/`intersecao` ao resultado do caminho por sequência. |
| Incompatibilidade com contrato da API | Usar `jsonify` ao invés de `json.dumps`. | Garantir todos os novos/alterados endpoints retornam `json.dumps(...)` conforme exigido. |

## Definição de pronto

- [x] **Catálogo persistido:** Sequências cadastradas via `POST /sequencias` permanecem no catálogo após reiniciar o container (com volume montado). As 6 originais são carregadas na inicialização.
- [x] **Cadastro funcional:** É possível cadastrar uma nova sequência ordenada por botões (anônimo), com validação de tamanho >= 2 e tratamento de duplicatas.
- [x] **Busca funcional:** Qualquer sequência cadastrada (originais + novas) pode ser usada em `GET /similares?sequencia=...`, retornando músicas que atendem às duas condições do matching.
- [x] **Regressão OK:** As 6 sequências originais continuam produzindo **exatamente** os mesmos resultados que produziam via `SEQ_FAMOSA` (validado contra `research/algoritmo/test_hipotese_sequencias_famosas.py`).
- [x] **Frontend atualizado:** `#/porsequencia` exibe catálogo real vindo do backend (sem hardcode de `sequencia1..sequencia4`), permite cadastro e busca por qualquer sequência.
- [x] **Restrições respeitadas:** Músicas/gêneros continuam do CSV em memória; uso de SQLite (stdlib); endpoints com `json.dumps(...)`; container único/local-only mantido.
- [x] **Documentação:** ADR 0002 existente e coerente com a implementação; alterações necessárias documentadas (volume para persistência).
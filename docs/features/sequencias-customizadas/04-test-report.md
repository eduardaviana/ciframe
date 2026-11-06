# Relatório de testes — Sequências de Acordes Customizadas

## Resumo

A cobertura automatizada agora cobre todo o caminho crítico da feature: banco e seed, persistência em volume Docker, matcher, catálogo, cadastro, validações de borda, duplicata, filtro de gênero, busca por sequência, paginação, ordenação, contrato `json.dumps(...)` e o fluxo principal do frontend em browser.

Todos os testes automatizados passaram:

- 5 scripts Python de backend/integração.
- 4 testes de browser com Playwright.
- Teste de persistência Docker com volume nomeado.

Os testes de rota e integração usam banco temporário via `SEQUENCIAS_DB_PATH` e não alteram `data/db/sequencias.db`.

## Escopo

Esta suíte é focada na feature de sequências customizadas (Passos 1–5) e na integração mínima com os endpoints legados que ela usa. Ela não é uma suíte completa do aplicativo: funcionalidades fora dessa feature não têm cobertura profunda, e os testes de contrato apenas verificam status, formato JSON e `Content-Type` dos endpoints existentes.

## Cobertura

| Passo | Teste | O que verifica | Resultado |
|---|---|---|---|
| 1 — banco e seed | `tests/test_passo1_exec_main.py` | Criação do diretório e arquivo do banco usando `SEQUENCIAS_DB_PATH` temporário; tabela `sequencias`; `UNIQUE`; seed das 6 originais; ausência de duplicatas; persistência de uma sequência customizada após nova inicialização; não toca no banco real. | Passou |
| 1 — persistência Docker | `tests/test_passo1_docker_persistence.py` | Constrói a imagem, sobe container com volume nomeado, cadastra `CEmFG`, remove/recria o container com o mesmo volume e confirma a persistência; sem volume, confirma que apenas as 6 originais são recriadas. Usa portas livres e limpa containers, volume e imagem. | Passou |
| 2 — matcher | `tests/test_passo2_matcher.py` | Regressão das 6 originais contra `SEQ_FAMOSA`, exigindo 0 divergências; ordem, contiguidade, subconjunto de acordes, sequência vazia, cifra vazia, sequência maior que a cifra e acordes repetidos. | Passou |
| 3 — rotas | `tests/test_passo3_routes.py` | `GET /sequencias`; `POST /sequencias`; catálogo ordenado por `id`; cadastro novo; duplicata 409; payload inválido, lista vazia, menos de 2 acordes e acorde não-string 400; mensagens de erro exatas; preservação de espaços/sem trim; ausência de limite máximo; busca da sequência recém-cadastrada; filtro `generos`; paginação; popularidade; ausência de `diferenca`/`intersecao`; sequência inexistente retorna `[]`; banco temporário isolado. | Passou |
| 4 — frontend | `tests/sequencia.spec.js` | Browser: catálogo carregado de `GET /sequencias`; abertura do modal; seleção de acordes; POST; toast; recarga do catálogo; busca pela sequência nova; duplicata inline; erro de rede; erro de catálogo; modal sem rolagem horizontal em 375px. | Passou |
| 4 — frontend visual | `tests/test_passo4_frontend.md` | Checklist manual permanece para detalhes visuais e de responsividade não cobertos pelo E2E. | Manual |
| 5 — integração | `tests/test_passo5_integration.py` | Remoção da função antiga baseada em `seqs_famosas`; busca funcionando com tags desativadas; músicas/gêneros ainda vindos do CSV em memória; banco temporário contendo somente a tabela `sequencias`; endpoints retornando JSON válido com `Content-Type: text/html`. | Passou |

## Teste de regressão obrigatório

A regressão compara, para cada uma das 6 sequências originais, o conjunto de músicas marcado na coluna `SEQ_FAMOSA` do CSV com o conjunto retornado por `musica_compatível_com_sequencia`.

| Sequência | Esperadas | Obtidas | Divergências |
|---|---:|---:|---:|
| `BmGDA` | 199 | 199 | 0 |
| `CGAmF` | 296 | 296 | 0 |
| `EmG` | 4 | 4 | 0 |
| `CA7DmG7` | 5 | 5 | 0 |
| `GmF` | 7 | 7 | 0 |
| `CC7FFm` | 3 | 3 | 0 |

Resultado: **0 divergências**. As rotas também foram verificadas contra os mesmos conjuntos esperados em `tests/test_passo3_routes.py` e `tests/test_passo5_integration.py`, incluindo o cenário em que todas as tags `seqs_famosas` são esvaziadas.

## Como rodar

Na raiz do repositório, instale as dependências uma vez:

```powershell
npm.cmd install
```

Para executar todos os testes automatizados (5 scripts Python + Playwright):

```powershell
npm.cmd test
```

O alias equivalente é `npm.cmd run test:all`.

Para executar apenas backend e persistência:

```powershell
py tests/test_passo1_exec_main.py
py tests/test_passo1_docker_persistence.py
py tests/test_passo2_matcher.py
py tests/test_passo3_routes.py
py tests/test_passo5_integration.py
```

Para executar apenas o frontend com Playwright:

```powershell
npm.cmd run test:frontend
```

O teste usa o Microsoft Edge instalado por padrão. Para outro canal do Playwright:

```powershell
$env:PW_CHANNEL="chrome"
npm.cmd run test:frontend
```

Para usar o Chromium baixado pelo Playwright, instale o browser e desative o canal fixo:

```powershell
npx.cmd playwright install chromium
$env:PW_CHANNEL="none"
npm.cmd run test:frontend
```

Checklist visual manual do frontend:

```powershell
py main.py
```

Abrir `http://localhost:5000/#/porsequencia` e seguir `tests/test_passo4_frontend.md`.

Persistência Docker manual (equivalente ao teste automatizado):

```powershell
docker build -t ciframe:test .
docker run -d --name ciframe-persist-test -p 18080:8080 -v "C:\caminho\para\db:/app/data/db" ciframe:test
```

Depois cadastrar uma sequência, remover o container com `docker rm -f ciframe-persist-test` e recriá-lo com o mesmo volume. A sequência deve continuar em `GET /sequencias`.

## O que ficou de fora

- **Detalhes visuais do frontend:** cores, alinhamento fino e comportamento em 768px/1280px continuam no checklist manual. O E2E cobre o fluxo funcional e a ausência de rolagem horizontal em 375px.
- **Dependência de CDN:** o frontend carrega AngularJS, jQuery e Bootstrap de CDN; o teste de browser precisa de rede para carregar esses recursos.
- **Docker indisponível:** `tests/test_passo1_docker_persistence.py` termina com `SKIP` em ambientes sem Docker, em vez de falhar.
- **Performance, concorrência e compatibilidade entre navegadores:** não foram testadas; não fazem parte do escopo funcional definido no plano.

## Avaliação de cobertura

**Backend: cobertura boa.** O caminho crítico está coberto, incluindo regressões completas, validações de borda, mensagens exatas e isolamento do banco real.

**Frontend: cobertura automatizada do fluxo principal.** O Playwright cobre catálogo, modal, cadastro, toast, busca, duplicata, erros e um cenário de responsividade. O checklist manual fica restrito a detalhes visuais.

**Persistência: cobertura automatizada.** O volume Docker é validado com remoção/recriação do container e com o cenário sem volume.

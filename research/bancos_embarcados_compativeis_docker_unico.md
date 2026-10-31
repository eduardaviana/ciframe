# Bancos embarcados compatíveis com container único e local-only

## Contexto (conforme ADR 0001)
- Deploy é **local-only via Docker** (`docs/adr/0001-local-only-docker-deploy.md:1,10-16`). 
- Dockerfile atual é **único estágio** e executa **um único processo**: `gunicorn --bind 0.0.0.0:8080 main:app` (`Dockerfile:1-12`).
- Não há `docker-compose`, múltiplos serviços ou orquestração. Tudo roda em **um único container**.
- Estado atual: **sem banco de dados**. Dados vêm de `data/top/dataset_final.csv` carregados em memória em `main.py:49-98` (`README.md:9`).
- Stack backend: Python 3.9, Flask 3.1, gunicorn (`main.py`, `requirements.txt`).

## Bancos embarcados viáveis (sem serviço externo adicional)
Os bancos abaixo rodam **in-process** ou com **arquivo local** dentro do mesmo container, sem precisar subir outro container/serviço separado. Todos são compatíveis com o modelo "único container local-only".

| Banco | Tipo | Persistência | Viabilidade no Docker único | Observações (apenas estado atual/compatibilidade) |
|---|---|---|---|---|
| **SQLite** | Embarcado (arquivo único `.sqlite`/`.db`) | Arquivo no filesystem do container (pode ser montado via volume para persistir entre reinícios) | **Alta**. É padrão, roda in-process com `sqlite3` (módulo built-in do Python) ou via `sqlite3`/`SQLAlchemy`. Não precisa de daemon. Cabe perfeitamente no único container. | Mais comum para "banco embarcado". Requer adicionar driver/ORM apenas se for utilizado. Hoje não está sendo usado. |
| **DuckDB** | Embarcado (analítico, arquivo único `.duckdb` ou in-memory) | Arquivo local ou in-memory. Suporta arquivo único. | **Alta**. Roda in-process (sem servidor), binário pequeno o suficiente para container slim. Funciona bem em único container local. | Bom para consultas analíticas em CSV/arquivos. Requer pacote `duckdb` se adicionado. Hoje não está sendo usado. |
| **LiteFS/just SQLite file** ou **UnQLite** / **Berkeley DB** (menos comuns) — mas os 3 principais: **SQLite**, **DuckDB**, **H2** (via `jaydebeapi`/`JPype` menos prático em Python puro) ou melhor focar em Python-friendly: **SQLite**, **DuckDB**, **sqlcipher** não necessário. Alternativa prática: **tinydb** (JSON-based, puro Python). | **tinydb**: arquivo JSON único (`db.json`) | Arquivo JSON local. Roda 100% em Python, sem dependências nativas complexas. | **Alta**. Extremamente simples, sem daemon, arquivo único. Perfeito para container único local. | É um banco "document" embarcado em arquivo JSON. Requer adicionar `tinydb` ao `requirements.txt` se utilizado. Hoje não está sendo usado. |

**Observação prática:** Dentre os três, **SQLite** é o mais "clássico" para substituir um modelo relacional simples mantendo tudo em arquivo local no mesmo container. **DuckDB** é viável para análise. **TinyDB** é viável para prototipagem sem SQL.

## Restrições do ambiente atual
- **Único container**: sem `docker-compose`, sem sidecars. Qualquer solução precisa rodar no mesmo processo/container ou em arquivo acessível pelo mesmo filesystem.
- **Local-only**: não há necessidade de cliente/servidor remoto, mas também não há configuração para isso.
- **Sem mudanças estruturais forçadas**: hoje tudo é em memória a partir de CSV (`main.py:49-98`). Se algum desses bancos fosse usado, precisaria ser adicionado (pacotes + inicialização) — mas isso não existe hoje.
- **Python 3.9 slim**: pacotes com binários nativos precisam ser compatíveis com a imagem base.

## Estado atual vs compatibilidade
- **Hoje:** nenhum banco embarcado em uso. Arquitetura 100% em memória + CSV.
- **Compatível com ADR 0001:** todos os três acima são compatíveis com "local-only via Docker" e "único container", pois não exigem serviço externo adicional.

## Referências concretas
- `docs/adr/0001-local-only-docker-deploy.md:1-16` (deploy local-only via Docker, sem cloud target, arquitetura in-memory CSV)
- `Dockerfile:1-12` (único container, único processo gunicorn)
- `README.md:8-9,13-21` (sem banco, comandos docker únicos)
- `main.py:49-98` (carregamento CSV em memória)
- `requirements.txt` (raiz, sem drivers de banco)
- `research/sem_banco_dados_e_docker.md` (documentação existente) 
- `research/docker_unico_e_banco_embarcado_existente.md` (documentação existente) 
- `research/codebase_research_20251028_pt.md` (pesquisa geral)
- `research/codebase_research_20251028.md` (pesquisa geral) 
- `AGENTS.md`
- `CONTRIB.md`
- `LICENSE` 
- `musica.py` 
- `static/index.html` 
- `static/assets/js/app.js`
- `static/assets/js/routes.js`
- `static/assets/js/controllers/*`
- `static/templates/*`
- `data/top/dataset_final.csv` (referenciado) 
- `research/*` (todos os arquivos)
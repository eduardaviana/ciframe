# Implicações dos 3 bancos embarcados para o Dockerfile atual e persistência

## Contexto (conforme estado atual)
- Dockerfile único estágio: `FROM python:3.9-slim`, instala `requirements.txt`, copia projeto, `EXPOSE 8080`, `CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]` (`Dockerfile:1-12`).
- Deploy local-only via Docker (`docs/adr/0001-local-only-docker-deploy.md`).
- Sem `docker-compose`, único container, único processo.
- Hoje sem banco: dados em memória a partir de `data/top/dataset_final.csv` (`main.py:49-98`, `README.md:9`). Estado perdido ao reiniciar o processo/container (carregado novamente na inicialização).

## Implicações por banco

| Banco | Implicações para o `Dockerfile` atual | Implicações para a persistência entre reinícios do container |
|---|---|---|
| **SQLite** | Adicionar dependência se usar ORM/driver (ex.: `SQLAlchemy` + `pysqlite3` já vem com stdlib `sqlite3` no Python; normalmente só precisa garantir que arquivo seja criado). Não precisa instalar servidor, não precisa de `apt` extra na maioria dos casos com `python:3.9-slim`. Se usar apenas `sqlite3` do stdlib, **nenhuma mudança obrigatória** no Dockerfile além de talvez criar diretório para o `.db`. | Persistência depende de **onde o arquivo `.db` é gravado**. Se gravado dentro do filesystem efêmero do container (ex.: `/app/data/app.db` sem volume), os dados são **perdidos ao remover/recriar o container**. Para persistir entre reinícios, é necessário montar um **volume** (ex.: `-v $(pwd)/data:/app/data`) apontando para o diretório onde o `.db` fica. O arquivo fica no host ou em volume nomeado. |
| **DuckDB** | Precisa adicionar `duckdb` ao `requirements.txt` (`RUN pip install ...`). Geralmente instala wheel/binário compatível com `python:3.9-slim`; pode não exigir pacotes `apt` adicionais. Dockerfile atual precisaria apenas dessa adição de dependência (e possivelmente diretório para arquivo `.duckdb`). | Arquivo único `.duckdb` gravado no filesystem. Sem volume montado, é efêmero (perdido ao recriar container). Com volume montado no diretório do arquivo, persiste entre reinícios. Também pode rodar em **in-memory** (sem persistência) dependendo da configuração. |
| **TinyDB** | Precisa adicionar `tinydb` ao `requirements.txt`. 100% Python, sem binários nativos complexos — mínimo impacto no `Dockerfile` (apenas linha de dependência). Não precisa de servidor. | Usa arquivo JSON único (ex.: `db.json`). Efêmero se dentro do container sem volume. Persiste entre reinícios apenas se o arquivo estiver em um **diretório montado via volume** ou em arquivo copiado/armazenado fora do layer efêmero. Também 100% em arquivo local. |

## Observação importante (estado atual)
Hoje **não há nenhuma dessas mudanças**. O Dockerfile não instala drivers de banco, não cria volumes no próprio Dockerfile (volumes são passados no `docker run` ou via orquestração), e não há lógica de persistência — tudo é recarregado do CSV em memória a cada inicialização. Qualquer um desses bancos, para ter persistência real entre reinícios do container, exigiria **montar um volume** no `docker run` apontando para o diretório onde o arquivo do banco fica. O Dockerfile por si só não garante persistência; ele apenas define a imagem.

## Referências concretas
- `Dockerfile:1-12`
- `docs/adr/0001-local-only-docker-deploy.md:1-16`
- `README.md:8-9,13-21`
- `main.py:49-98`
- `requirements.txt` (raiz)
- `research/bancos_embarcados_compativeis_docker_unico.md`
- `research/sem_banco_dados_e_docker.md`
- `research/docker_unico_e_banco_embarcado_existente.md`
- `research/codebase_research_20251028_pt.md`
- `research/codebase_research_20251028.md`
- `AGENTS.md`, `CONTRIB.md`, `LICENSE`
- `musica.py`, `static/*`, `data/top/dataset_final.csv` 
- `research/*` (todos os arquivos) 
- `scripts/build-chords-transitions.R`
- `docs/features/sequencias-customizadas/01-research.md`
- `docs/adr/0002-frontend-angularjs-legacy.md`
- `docs/adr/0003-lift-frontend-freeze.md`
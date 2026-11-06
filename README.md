# deciframe

Descubra as músicas que você já sabe tocar (e ainda não faz ideia). Busque por
título/artista, gênero, pelos acordes que você já manja, ou por sequências de
acordes famosas — o deciframe cruza isso com uma base de cifras e sugere
músicas parecidas.

Stack: backend Flask (Python) servindo uma API JSON + um frontend AngularJS
estático. Músicas e gêneros continuam sendo carregados do CSV em memória, e o
catálogo de sequências de acordes é persistido em SQLite (`sqlite3` da
biblioteca padrão).

## Rodando localmente

### Com Docker

```
docker build -t ciframe .
docker run -p 8080:8080 -v "$(pwd)/data/db:/app/data/db" ciframe
```

No PowerShell:

```powershell
docker run -p 8080:8080 -v "${PWD}/data/db:/app/data/db" ciframe
```

O volume em `data/db` é o que preserva as sequências customizadas. Sem ele, as
6 sequências originais são recriadas na inicialização, mas sequências
cadastradas por usuários são perdidas quando o container é removido ou recriado.

Acesse [http://localhost:8080](http://localhost:8080).

### Com virtualenv

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Acesse [http://localhost:5000](http://localhost:5000).

O caminho do banco pode ser alterado pela variável de ambiente
`SEQUENCIAS_DB_PATH`:

```bash
SEQUENCIAS_DB_PATH=/caminho/para/sequencias.db python main.py
```

No PowerShell:

```powershell
$env:SEQUENCIAS_DB_PATH = "C:\caminho\para\sequencias.db"
python main.py
```

---

Para convenções de contribuição, veja [CONTRIB.md](CONTRIB.md). Licença: [LICENSE](LICENSE).

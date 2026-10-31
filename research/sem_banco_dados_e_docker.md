# Sem banco de dados e uso do Docker

## Resumo (3-6 frases)
Não há banco de dados no projeto. Conforme `README.md:9`, a base de dados é carregada de um CSV em memória (sem banco). Em `main.py:49-98`, o arquivo `data/top/dataset_final.csv` é lido na inicialização, os objetos `Musica` são criados e tudo fica armazenado em estruturas em memória (`musicas_dict`, `musicas` como `OrderedDict`, `genero_musicas`, `generos`, `acordes`). O Docker é sim usado para subir o servidor, mas não por causa de banco de dados — é apenas um meio de empacotar e executar a aplicação Flask com `gunicorn`.

## Sem banco de dados
- `README.md:9`: "numa base de dados carregada de um CSV em memória (sem banco)."
- `main.py:49`: abre `data/top/dataset_final.csv` e lê na inicialização (`main.py:49-98`).
- `main.py:74`: armazena em `musicas_dict[musica_obj.id_unico_musica] = musica_obj`
- `main.py:88-89`: cria `musicas = OrderedDict(sorted(musicas_dict.items(), key=lambda x: x[1].popularidade, reverse=True))`
- `main.py:82-85`: constrói `genero_musicas` por gênero
- `main.py:66,77-78,92`: mantém `generos` e `acordes` em memória
- Não existem imports/uso de SQLAlchemy, sqlite, postgres, etc. em `main.py` ou `requirements.txt`.

## Docker para subir o servidor
- `README.md:13-21`: instruções com `docker build -t ciframe .` e `docker run -p 8080:8080 ciframe`, acessando em `http://localhost:8080`.
- `Dockerfile:1-12`:
  ```dockerfile
  FROM python:3.9-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY . .
  EXPOSE 8080
  CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
  ```
- O comando para subir o servidor via Docker é exatamente `docker run -p 8080:8080 ciframe` (após build), executando `gunicorn` na porta 8080 com `main:app`. 
- Alternativa com virtualenv: `python main.py` sobe na porta 5000 (`README.md:22-31`).

**Resposta direta:** Correto no sentido de que existe um comando Docker para subir o servidor. Mas **não** é por causa de banco de dados — não há banco de dados no projeto. O Docker apenas empacota a aplicação Flask com gunicorn servindo a API + arquivos estáticos, com todos os dados já carregados do CSV em memória na inicialização.

## Referências concretas
- `README.md:8-9,13-31`
- `Dockerfile:1-12`
- `main.py:49-98`
- `requirements.txt` (presente na raiz)
# coding: utf-8
"""Valida a limpeza e integração do Passo 5.

Cobre:
1. A busca por sequência não depende mais das tags `SEQ_FAMOSA`.
2. As 6 sequências originais continuam funcionando via catálogo do SQLite.
3. Músicas e gêneros continuam vindo do CSV em memória.
4. Os endpoints de API continuam retornando `json.dumps(...)`.

O teste usa banco temporário e não altera `data/db/sequencias.db`.

Uso (a partir da raiz do repositório):
    py tests/test_passo5_integration.py
"""

import builtins
import json
import os
import sqlite3
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

# Isola o banco do teste: não usa nem altera data/db/sequencias.db.
_TMP_DIR = tempfile.TemporaryDirectory(prefix='deciframe_passo5_')
os.environ['SEQUENCIAS_DB_PATH'] = os.path.join(_TMP_DIR.name, 'sequencias.db')

# No Windows o main.py abre o CSV com o encoding do locale (cp1252), mas o
# arquivo é UTF-8. Força UTF-8 só na leitura do CSV, sem alterar main.py.
_open_original = builtins.open


def _abrir_csv_com_utf8(arquivo, modo='r', *args, **kwargs):
    if (isinstance(arquivo, str)
            and arquivo.replace('\\', '/').endswith('data/top/dataset_final.csv')
            and 'b' not in modo
            and 'encoding' not in kwargs):
        kwargs['encoding'] = 'utf-8'
    return _open_original(arquivo, modo, *args, **kwargs)


builtins.open = _abrir_csv_com_utf8
import main  # noqa: E402  (precisa vir depois do ajuste de encoding)
builtins.open = _open_original

SEQUENCIAS = [
    ('BmGDA', ['Bm', 'G', 'D', 'A']),
    ('CGAmF', ['C', 'G', 'Am', 'F']),
    ('EmG', ['Em', 'G']),
    ('CA7DmG7', ['C', 'A7', 'Dm', 'G7']),
    ('GmF', ['Gm', 'F']),
    ('CC7FFm', ['C', 'C7', 'F', 'Fm']),
]

falhas = []


def checar(condicao, mensagem):
    if condicao:
        print('  OK:', mensagem)
    else:
        print('  FALHA:', mensagem)
        falhas.append(mensagem)


def json_da_resposta(resposta):
    return json.loads(resposta.data.decode('utf-8'))


def buscar_todas_as_paginas(cliente, sequencia):
    itens = []
    pagina = 1
    while True:
        resposta = cliente.get(
            '/similares',
            query_string={
                'sequencia': ','.join(sequencia),
                'pagina': str(pagina),
            },
        )
        checar(resposta.status_code == 200,
               '%s página %d responde 200' % (''.join(sequencia), pagina))
        itens_da_pagina = json_da_resposta(resposta)
        itens.extend(itens_da_pagina)
        if len(itens_da_pagina) < main.TAM_PAGINA:
            break
        pagina += 1
    return itens


def testar_busca_sem_tags_seq_famosa():
    print('\n[1] Busca por sequência sem depender de SEQ_FAMOSA')
    cliente = main.app.test_client()

    checar(not hasattr(main, 'get_similares_por_sequencia'),
           'função antiga que usava seqs_famosas foi removida')

    tags_originais = {
        musica.id_unico_musica: musica.seqs_famosas
        for musica in main.musicas.values()
    }
    try:
        for musica in main.musicas.values():
            musica.seqs_famosas = []

        for nome, acordes in SEQUENCIAS:
            esperadas = {
                musica.id_unico_musica
                for musica in main.musicas.values()
                if main.musica_compatível_com_sequencia(musica, acordes)
            }
            obtidas = buscar_todas_as_paginas(cliente, acordes)
            ids_obtidos = {item['id_unico_musica'] for item in obtidas}

            popularidades = [item['popularidade'] for item in obtidas]
            ordenado_por_popularidade = all(
                popularidades[i] >= popularidades[i + 1]
                for i in range(len(popularidades) - 1)
            )

            checar(ids_obtidos == esperadas,
                   '%s continua igual ao matcher com tags desativadas' % nome)
            checar(ordenado_por_popularidade,
                   '%s continua ordenada por popularidade' % nome)

            if ids_obtidos != esperadas:
                print('    faltaram:', sorted(esperadas - ids_obtidos)[:5])
                print('    a mais  :', sorted(ids_obtidos - esperadas)[:5])

            if obtidas:
                checar('diferenca' not in obtidas[0] and 'intersecao' not in obtidas[0],
                       '%s não adiciona diferenca/intersecao' % nome)
    finally:
        for musica in main.musicas.values():
            musica.seqs_famosas = tags_originais[musica.id_unico_musica]


def testar_dados_do_csv():
    print('\n[2] Músicas e gêneros continuam carregados do CSV em memória')
    checar(len(main.musicas) > 0, 'músicas carregadas em memória')
    checar(len(main.generos) > 0, 'gêneros carregados em memória')

    conn = sqlite3.connect(main.DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        tabelas = {row[0] for row in cur.fetchall()}
    finally:
        conn.close()

    checar(tabelas == {'sequencias'},
           'banco contém apenas a tabela sequencias')

    cliente = main.app.test_client()
    resposta_musicas = cliente.get('/musicas')
    resposta_generos = cliente.get('/generos')

    checar(resposta_musicas.status_code == 200,
           'GET /musicas responde 200')
    checar(resposta_generos.status_code == 200,
           'GET /generos responde 200')
    checar(len(json_da_resposta(resposta_musicas)) == len(main.musicas),
           'GET /musicas devolve as músicas em memória')
    checar(set(json_da_resposta(resposta_generos)) == set(main.generos),
           'GET /generos devolve os gêneros em memória')


def testar_endpoints_json_dumps():
    print('\n[3] Endpoints de API continuam retornando json.dumps')
    cliente = main.app.test_client()
    id_musica = next(iter(main.musicas))

    casos = [
        ('GET /search', cliente.get('/search', query_string={'key': 'a'})),
        ('GET /musicas', cliente.get('/musicas')),
        ('GET /generos', cliente.get('/generos')),
        ('GET /acordes', cliente.get('/acordes')),
        ('GET /sequencias', cliente.get('/sequencias')),
        ('GET /musica/<id>/', cliente.get('/musica/%s/' % id_musica)),
        ('GET /similares', cliente.get('/similares')),
        ('GET /similares?sequencia=...', cliente.get(
            '/similares', query_string={'sequencia': 'Bm,G,D,A'})),
        ('POST /sequencias inválido', cliente.post(
            '/sequencias', json={'sequencia': ['Em']})),
    ]

    for descricao, resposta in casos:
        checar(resposta.status_code in (200, 400),
               '%s responde com status esperado (200/400)' % descricao)
        checar(resposta.mimetype == 'text/html',
               '%s não usa jsonify (Content-Type text/html)' % descricao)
        try:
            json_da_resposta(resposta)
            parseavel = True
        except Exception:
            parseavel = False
        checar(parseavel, '%s devolve JSON válido' % descricao)

    acordes = ['ZzPasso5Teste', 'YyPasso5Teste']
    chave = ''.join(acordes)
    conn = sqlite3.connect(main.DB_PATH)
    try:
        conn.execute('DELETE FROM sequencias WHERE sequencia = ?', (chave,))
        conn.commit()

        resposta = cliente.post('/sequencias', json={'sequencia': acordes})
        checar(resposta.status_code == 200, 'POST /sequencias válido responde 200')
        checar(resposta.mimetype == 'text/html',
               'POST /sequencias válido não usa jsonify')
        checar(json_da_resposta(resposta).get('sequencia') == chave,
               'POST /sequencias válido devolve JSON válido')

        duplicada = cliente.post('/sequencias', json={'sequencia': acordes})
        checar(duplicada.status_code == 409,
               'POST /sequencias duplicado responde 409')
        checar(duplicada.mimetype == 'text/html',
               'POST /sequencias duplicado não usa jsonify')
        checar('erro' in json_da_resposta(duplicada),
               'POST /sequencias duplicado devolve JSON com erro')
    finally:
        conn.execute('DELETE FROM sequencias WHERE sequencia = ?', (chave,))
        conn.commit()
        conn.close()


if __name__ == '__main__':
    testar_busca_sem_tags_seq_famosa()
    testar_dados_do_csv()
    testar_endpoints_json_dumps()

    print('\n' + '=' * 60)
    if falhas:
        print('%d verificação(ões) falharam.' % len(falhas))
        sys.exit(1)
    print('PASSO 5 VALIDADO COM SUCESSO!')

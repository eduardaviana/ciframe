# coding: utf-8
"""Valida as rotas do Passo 3.

Cobre:
1. `GET /similares?sequencia=...` usando o catálogo do SQLite e o matcher.
2. Filtro opcional `generos`.
3. `GET /sequencias` retornando o catálogo completo.
4. `POST /sequencias` cadastrando uma sequência nova e a usando em `/similares`.
5. Preservação de acordes sem trim e ausência de limite máximo.
6. Validações do `POST /sequencias` (payload inválido, menos de 2 acordes,
   acorde não-string e sequência duplicada), com mensagens exatas.

O teste usa banco temporário e não altera `data/db/sequencias.db`.

Uso (a partir da raiz do repositório):
    py tests/test_passo3_routes.py
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
_TMP_DIR = tempfile.TemporaryDirectory(prefix='deciframe_passo3_')
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


def buscar_todas_as_paginas(cliente, sequencia, generos=None):
    itens = []
    pagina = 1
    while True:
        query_string = {
            'sequencia': ','.join(sequencia),
            'pagina': str(pagina),
        }
        if generos:
            query_string['generos'] = generos
        resposta = cliente.get('/similares', query_string=query_string)
        checar(resposta.status_code == 200,
               '%s página %d responde 200' % (''.join(sequencia), pagina))
        itens_da_pagina = json.loads(resposta.data.decode('utf-8'))
        itens.extend(itens_da_pagina)
        if len(itens_da_pagina) < main.TAM_PAGINA:
            break
        pagina += 1
    return itens


def buscar_catalogo(cliente):
    resposta = cliente.get('/sequencias')
    checar(resposta.status_code == 200, 'GET /sequencias responde 200')
    return json.loads(resposta.data.decode('utf-8'))


def testar_similares_por_sequencia():
    print('\n[1] GET /similares?sequencia=... (6 sequências originais)')
    cliente = main.app.test_client()

    for indice, (nome, acordes) in enumerate(SEQUENCIAS):
        esperadas = [
            m for m in main.musicas.values()
            if str(indice) in m.seqs_famosas
        ]
        obtidas = buscar_todas_as_paginas(cliente, acordes)

        ids_esperados = {m.id_unico_musica for m in esperadas}
        ids_obtidos = {item['id_unico_musica'] for item in obtidas}
        popularidades = [item['popularidade'] for item in obtidas]
        ordenado_por_popularidade = all(
            popularidades[i] >= popularidades[i + 1]
            for i in range(len(popularidades) - 1)
        )

        checar(ids_obtidos == ids_esperados,
               '%s retorna exatamente o conjunto esperado' % nome)
        checar(ordenado_por_popularidade,
               '%s retorna em ordem decrescente de popularidade' % nome)
        if ids_obtidos != ids_esperados:
            print('    faltaram:', sorted(ids_esperados - ids_obtidos)[:5])
            print('    a mais  :', sorted(ids_obtidos - ids_esperados)[:5])

        if obtidas:
            checar('diferenca' not in obtidas[0] and 'intersecao' not in obtidas[0],
                   '%s não adiciona diferenca/intersecao' % nome)

    resposta = cliente.get('/similares', query_string={'sequencia': 'XYZ'})
    checar(json.loads(resposta.data.decode('utf-8')) == [],
           'sequência inexistente retorna lista vazia')


def testar_filtro_genero():
    print('\n[2] GET /similares?sequencia=...&generos=...')
    cliente = main.app.test_client()
    acordes = ['Bm', 'G', 'D', 'A']

    genero_escolhido = None
    esperadas = set()
    for genero in main.generos:
        candidatas = {
            musica.id_unico_musica
            for musica in main.musicas.values()
            if musica.genero == genero
            and main.musica_compatível_com_sequencia(musica, acordes)
        }
        if candidatas:
            genero_escolhido = genero
            esperadas = candidatas
            break

    checar(genero_escolhido is not None,
           'há gênero com resultados para testar o filtro')

    if genero_escolhido is None:
        return

    print('  Gênero usado no teste:', genero_escolhido)
    obtidas = buscar_todas_as_paginas(cliente, acordes, generos=genero_escolhido)
    ids_obtidos = {item['id_unico_musica'] for item in obtidas}

    checar(ids_obtidos == esperadas,
           'filtro de gênero retorna exatamente as músicas esperadas')
    checar(all(item['genero'] == genero_escolhido for item in obtidas),
           'todas as músicas retornadas pertencem ao gênero filtrado')


def testar_catalogo():
    print('\n[3] GET /sequencias')
    cliente = main.app.test_client()
    catalogo = buscar_catalogo(cliente)

    por_chave = {item['sequencia']: item for item in catalogo}
    for nome, acordes in SEQUENCIAS:
        item = por_chave.get(nome)
        checar(item is not None, '%s está no catálogo' % nome)
        if item:
            checar(item['acordes'] == ';'.join(acordes),
                   '%s tem os acordes no formato esperado' % nome)
            checar(isinstance(item['id'], int),
                   '%s tem id inteiro' % nome)

    ids = [item['id'] for item in catalogo]
    checar(ids == sorted(ids), 'catálogo ordenado por id')
    checar(len(ids) == len(set(ids)), 'catálogo sem ids duplicados')


def testar_cadastro_e_busca():
    print('\n[4] POST /sequencias + GET /similares com sequência nova')
    cliente = main.app.test_client()
    acordes = ['Em', 'G', 'Ab']
    chave = ''.join(acordes)

    conn = sqlite3.connect(main.DB_PATH)
    try:
        conn.execute('DELETE FROM sequencias WHERE sequencia = ?', (chave,))
        conn.commit()

        resposta = cliente.post('/sequencias', json={'sequencia': acordes})
        checar(resposta.status_code == 200, 'POST /sequencias responde 200')
        cadastrada = json.loads(resposta.data.decode('utf-8'))
        checar(cadastrada.get('sequencia') == chave,
               'POST /sequencias retorna a chave concatenada')
        checar(cadastrada.get('acordes') == ';'.join(acordes),
               'POST /sequencias retorna os acordes separados por ;')
        checar(isinstance(cadastrada.get('id'), int),
               'POST /sequencias retorna id inteiro')

        catalogo = buscar_catalogo(cliente)
        item = next((x for x in catalogo if x['sequencia'] == chave), None)
        checar(item is not None and item['id'] == cadastrada['id'],
               'sequência nova aparece no catálogo')

        obtidas = buscar_todas_as_paginas(cliente, acordes)
        esperadas = {
            m.id_unico_musica
            for m in main.musicas.values()
            if main.musica_compatível_com_sequencia(m, acordes)
        }
        checar({item['id_unico_musica'] for item in obtidas} == esperadas,
               'GET /similares usa a sequência cadastrada no banco')

        duplicada = cliente.post('/sequencias', json={'sequencia': acordes})
        checar(duplicada.status_code == 409,
               'POST /sequencias recusa sequência duplicada com 409')
        checar(json.loads(duplicada.data.decode('utf-8')) == {
            'erro': 'sequência já cadastrada'
        }, 'erro de duplicata tem a mensagem esperada')
    finally:
        conn.execute('DELETE FROM sequencias WHERE sequencia = ?', (chave,))
        conn.commit()
        conn.close()


def testar_armazenamento_sem_normalizacao():
    print('\n[5] POST /sequencias preserva acordes e não impõe limite máximo')
    cliente = main.app.test_client()
    conn = sqlite3.connect(main.DB_PATH)
    casos = [
        ('espaços não são removidos', [' C ', 'G'], ' C ;G'),
        ('não há limite máximo de acordes', ['C'] * 120, ';'.join(['C'] * 120)),
    ]

    try:
        for descricao, acordes, acordes_str in casos:
            chave = ''.join(acordes)
            conn.execute('DELETE FROM sequencias WHERE sequencia = ?', (chave,))
            conn.commit()

            resposta = cliente.post('/sequencias', json={'sequencia': acordes})
            checar(resposta.status_code == 200,
                   '%s: POST responde 200' % descricao)

            dados = json.loads(resposta.data.decode('utf-8'))
            checar(dados.get('sequencia') == chave,
                   '%s: chave concatenada é preservada' % descricao)
            checar(dados.get('acordes') == acordes_str,
                   '%s: acordes são preservados sem normalização' % descricao)

            conn_leitura = sqlite3.connect(main.DB_PATH)
            try:
                row = conn_leitura.execute(
                    'SELECT acordes FROM sequencias WHERE sequencia = ?',
                    (chave,)
                ).fetchone()
            finally:
                conn_leitura.close()

            checar(row is not None and row[0] == acordes_str,
                   '%s: banco guarda os acordes exatamente como recebidos' % descricao)

            conn.execute('DELETE FROM sequencias WHERE sequencia = ?', (chave,))
            conn.commit()
    finally:
        for _, acordes, _ in casos:
            conn.execute(
                'DELETE FROM sequencias WHERE sequencia = ?',
                (''.join(acordes),)
            )
        conn.commit()
        conn.close()


def testar_validacoes_post():
    print('\n[6] Validações do POST /sequencias')
    cliente = main.app.test_client()

    erro_payload = 'informe a lista de acordes em "sequencia"'
    erro_tamanho = 'a sequência deve ser uma lista com pelo menos 2 acordes'
    erro_tipo = 'todos os acordes devem ser strings'

    casos = [
        ('sem JSON válido', cliente.post(
            '/sequencias', data='{', content_type='application/json'),
         erro_payload),
        ('payload é uma lista', cliente.post(
            '/sequencias', json=[]),
         erro_payload),
        ('sem a chave sequencia', cliente.post(
            '/sequencias', json={}),
         erro_payload),
        ('sequencia não é lista', cliente.post(
            '/sequencias', json={'sequencia': 'EmG'}),
         erro_tamanho),
        ('lista vazia', cliente.post(
            '/sequencias', json={'sequencia': []}),
         erro_tamanho),
        ('menos de 2 acordes', cliente.post(
            '/sequencias', json={'sequencia': ['Em']}),
         erro_tamanho),
        ('acorde não-string', cliente.post(
            '/sequencias', json={'sequencia': ['Em', 1]}),
         erro_tipo),
    ]

    for descricao, resposta, mensagem in casos:
        checar(resposta.status_code == 400,
               '%s retorna 400' % descricao)
        checar(json.loads(resposta.data.decode('utf-8')) == {
            'erro': mensagem
        }, '%s retorna a mensagem de erro esperada' % descricao)


if __name__ == '__main__':
    testar_similares_por_sequencia()
    testar_filtro_genero()
    testar_catalogo()
    testar_cadastro_e_busca()
    testar_armazenamento_sem_normalizacao()
    testar_validacoes_post()

    print('\n' + '=' * 60)
    if falhas:
        print('%d verificação(ões) falharam.' % len(falhas))
        sys.exit(1)
    print('PASSO 3 VALIDADO COM SUCESSO!')

# coding: utf-8
import json
from flask import Flask, request
import sys
import os
import sqlite3
from musica import *
from collections import OrderedDict
import unicodedata

app = Flask(__name__)

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'db')
DB_PATH = os.path.join(DB_DIR, 'sequencias.db')

def init_db():
    try:
        if not os.path.exists(DB_DIR):
            os.makedirs(DB_DIR)
    except Exception:
        pass
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS sequencias (
        id INTEGER PRIMARY KEY,
        sequencia TEXT UNIQUE,
        acordes TEXT
    )''')
    conn.commit()
    return conn

def seed_sequencias():
    conn = init_db()
    cur = conn.cursor()
    originais = [
        ('BmGDA', 'Bm;G;D;A'),
        ('CGAmF', 'C;G;Am;F'),
        ('EmG', 'Em;G'),
        ('CA7DmG7', 'C;A7;Dm;G7'),
        ('GmF', 'Gm;F'),
        ('CC7FFm', 'C;C7;F;Fm'),
    ]
    for seq, acordes_str in originais:
        try:
            cur.execute('INSERT OR IGNORE INTO sequencias (sequencia, acordes) VALUES (?, ?)', (seq, acordes_str))
        except Exception:
            pass
    conn.commit()
    conn.close()

init_db()
seed_sequencias()

def limpa_cifra(raw_cifra):
    cifra = []
    for m in raw_cifra:
        if m.strip() != '':
            # filtra tablaturas
            if '|' in m:
                acorde = m.split('|')[0].split()[0]
                cifra.append(acorde)
            # lida com acordes separados por espaço
            else:
                tokens = [token for token in m.split()]
                cifra += tokens
    return cifra

# colunas do csv
ARTISTA_ID = 0
MUSICA_ID = 1
ARTISTA = 2
MUSICA = 3
GENERO = 4
POPULARIDADE = 5
TOM = 6
SEQ_FAMOSA = 7
CIFRA = 8
TAM_PAGINA = 100

genero_musicas = {}
generos = set()
acordes = set()
sequencias = {}

musicas_dict = {}

f = open('data/top/dataset_final.csv')
f.readline()

for line in f:
    line = line.replace('"', '').replace('NA', '')[:-1]

    musica = line.split(',')
    musica[POPULARIDADE] = int(musica[POPULARIDADE].replace('.', ''))

    if musica[CIFRA] != '':
        musica[CIFRA] = limpa_cifra(musica[CIFRA].split(';'))
    else:
        musica[CIFRA] = []

    musica[SEQ_FAMOSA] = musica[SEQ_FAMOSA].split(";")

    # conjunto único de gêneros
    generos.add(musica[GENERO])

    # inclui música no dict de músicas
    musica_obj = Musica(musica[ARTISTA_ID], musica[ARTISTA],
            musica[MUSICA_ID], musica[MUSICA], musica[GENERO],
            int(musica[POPULARIDADE]), musica[SEQ_FAMOSA],
            musica[TOM], musica[CIFRA])

    musicas_dict[musica_obj.id_unico_musica] = musica_obj

    # conjunto único de acordes
    for acorde in musica_obj.acordes:
        acordes.add(acorde)

    # constrói dict mapeando gênero para músicas
    # deve ser usado para melhorar o desempenho das buscas
    if musica_obj.genero in genero_musicas:
        genero_musicas[musica_obj.genero].append(musica_obj)
    else:
        genero_musicas[musica_obj.genero] = [musica_obj]

# dicionário de músicas cujos valores são ordenados por popularidade
musicas = OrderedDict(sorted(musicas_dict.items(),
    key=lambda x: x[1].popularidade, reverse = True))

# para trabalhar melhor com json
generos = list(generos)

# ordena genero_musicas por popularidade
for k,v in genero_musicas.items():
    genero_musicas[k].sort(key = lambda x : x.popularidade, reverse = True)

f.close()


@app.route('/')
def index():
    return app.send_static_file('index.html')
''' Busca por músicas que possuem no título ou no nome do artista o argumento passado por key.
params: key e generos (opcional). Caso generos não sejam definidos, a busca não irá filtrar por gênero.
exemplo 1: /search?key=no dia em que eu saí de casa
exemplo 2: /search?key=no dia em que eu saí de casa&generos=Rock,Samba '''

@app.route('/<path:path>')
def static_proxy(path):
  # send_static_file will guess the correct MIME type
  return app.send_static_file(path)

@app.route('/search')
def busca():
    generos_tag = request.args.get('generos', [])
    pagina_tag = request.args.get('pagina','1')
    keys = request.args.get('key').lower()
    keys = remover_combinantes(keys).split(' ')

    generos_key = generos
    if generos_tag:
        generos_key = generos_tag.split(',')

    collection = apply_filtro(musicas.values(), generos_key)
    out = []

    for musica in collection:
        text = '%s %s' % (musica.nome_artista.lower(), musica.nome_musica.lower())
        text_list = remover_combinantes(text).split(' ')
        if all(key in text_list for key in keys):
            matches = {
                'id_unico_musica' : musica.id_unico_musica,
                'id_artista' : musica.id_artista,
                'id_musica' : musica.id_musica,
                'nome_artista' : musica.nome_artista,
                'nome_musica' : musica.nome_musica,
                'genero' : musica.genero,
                'url' : musica.url,
            }
            out.append(matches)
    return json.dumps(get_pagina(out, pagina_tag))

# cópia
def remover_combinantes(string):
    string = unicodedata.normalize('NFD', string)
    return u''.join(ch for ch in string if unicodedata.category(ch) != 'Mn')

''' Retorna as músicas armazenadas no sistema (ordenados por popularidade).
    O serviço é paginado. Cada página tem tamanho 100, por default.
    params: pagina. Caso não seja definida a página, o valor default é 1.
    exemplo 1: /musica?pagina=2
    exemplo 2: /musica'''
@app.route('/musicas')
def get_musicas():
    return json.dumps([v.__dict__ for v in musicas.values()])

@app.route('/generos')
def get_generos():
    return json.dumps(generos)

@app.route('/acordes')
def get_acordes():
    return json.dumps(list(acordes))

@app.route('/sequencias')
def get_sequencias():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, sequencia, acordes FROM sequencias ORDER BY id')
    rows = cur.fetchall()
    conn.close()
    return json.dumps([
        {'id': row[0], 'sequencia': row[1], 'acordes': row[2]}
        for row in rows
    ])

@app.route('/sequencias', methods=['POST'])
def post_sequencias():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or 'sequencia' not in payload:
        return json.dumps({'erro': 'informe a lista de acordes em "sequencia"'}), 400

    acordes_lista = payload['sequencia']
    if not isinstance(acordes_lista, list) or len(acordes_lista) < 2:
        return json.dumps({'erro': 'a sequência deve ser uma lista com pelo menos 2 acordes'}), 400

    if not all(isinstance(acorde, str) for acorde in acordes_lista):
        return json.dumps({'erro': 'todos os acordes devem ser strings'}), 400

    sequencia = ''.join(acordes_lista)
    acordes_str = ';'.join(acordes_lista)

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO sequencias (sequencia, acordes) VALUES (?, ?)',
            (sequencia, acordes_str)
        )
        conn.commit()
        novo_id = cur.lastrowid
    except sqlite3.IntegrityError:
        conn.rollback()
        return json.dumps({'erro': 'sequência já cadastrada'}), 409
    finally:
        conn.close()

    return json.dumps({
        'id': novo_id,
        'sequencia': sequencia,
        'acordes': acordes_str,
    })

@app.route('/musica/<m_id>/')
def get_musica(m_id):
    return json.dumps(musicas[m_id].__dict__)

def sequencia_aparece_em_cifra(sequencia_lista, cifra_lista):
    if not sequencia_lista:
        return False
    if not cifra_lista:
        return False
    seq_len = len(sequencia_lista)
    cifra_len = len(cifra_lista)
    if seq_len > cifra_len:
        return False
    for i in range(cifra_len - seq_len + 1):
        match = True
        for j in range(seq_len):
            if cifra_lista[i + j] != sequencia_lista[j]:
                match = False
                break
        if match:
            return True
    return False

def musica_compatível_com_sequencia(musica, sequencia_lista):
    if not sequencia_aparece_em_cifra(sequencia_lista, musica.cifra):
        return False
    musica_acordes_set = set(musica.acordes)
    seq_set = set(sequencia_lista)
    if musica_acordes_set.issubset(seq_set):
        return True
    return False

def get_similares_por_sequencia_db(sequencia_lista, generos_key):
    collection = apply_filtro(musicas.values(), generos_key)
    similares = []
    for musica in collection:
        if musica_compatível_com_sequencia(musica, sequencia_lista):
            similar = {
                'id_unico_musica': musica.id_unico_musica,
                'id_artista': musica.id_artista,
                'id_musica': musica.id_musica,
                'nome_artista': musica.nome_artista,
                'nome_musica': musica.nome_musica,
                'popularidade': musica.popularidade,
                'acordes': musica.acordes,
                'genero': musica.genero,
                'url': musica.url,
            }
            similares.append(similar)
    similares.sort(key=lambda x: x['popularidade'], reverse=True)
    return similares

@app.route('/similares')
def get_similares():
    # tratando request
    acordes_tag = request.args.get('acordes')
    id_musica_tag = request.args.get('id_unico_musica')
    sequencia_tag = request.args.get('sequencia')
    pagina_tag = request.args.get('pagina','1')

    # se não existir, filtra por todos.
    generos_tag = request.args.get('generos')
    generos_key = generos
    if generos_tag:
        generos_key = generos_tag.split(',')

    acordes = []
    if acordes_tag:
        acordes = acordes_tag.split(',')
    elif id_musica_tag:
        musica = musicas[id_musica_tag]
        acordes = musica.acordes
    elif sequencia_tag:
        seq_key = sequencia_tag.replace(',', '')
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT sequencia, acordes FROM sequencias WHERE sequencia = ?', (seq_key,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return json.dumps([])
        acordes_lista = row[1].split(';') if row[1] else []
        similares = get_pagina(get_similares_por_sequencia_db(acordes_lista, generos_key), pagina_tag)
        return json.dumps(similares)

    similares = get_similares(acordes, generos_key, id_musica_tag)

    return json.dumps(get_pagina(similares, pagina_tag))

def get_similares_por_sequencia(id_seq, generos_key):
    # filtra para melhor desempenho
    collection = apply_filtro(musicas.values(), generos_key)

    similares = []
    for musica in collection:
        if str(id_seq) in musica.seqs_famosas:
            similar = {
                'id_unico_musica' : musica.id_unico_musica,
                'id_artista' : musica.id_artista,
                'id_musica' : musica.id_musica,
                'nome_artista' : musica.nome_artista,
                'nome_musica' : musica.nome_musica,
                'popularidade' : musica.popularidade,
                'acordes' : musica.acordes,
                'genero' : musica.genero,
                'url' : musica.url,
            }
            similares.append(similar)

    return similares


def get_pagina(colecao, pagina_tag):
    sl = (int(pagina_tag) - 1)*TAM_PAGINA
    return colecao[sl:sl+TAM_PAGINA]

def get_similares(acordes, generos_key, id_musica = None):

    # filtra para melhor desempenho
    collection = apply_filtro(musicas.values(), generos_key)

    similares = []
    for musica in collection:

        if musica.id_unico_musica != id_musica:

            inter = set(acordes).intersection(set(musica.acordes))
            diff = set(musica.acordes) - set(acordes)

            # somente as que tiverem interseção e as que forem
            # dos generos solicitados.
            if len(inter) > 0:
                similar = {
                        'id_unico_musica' : musica.id_unico_musica,
                        'id_artista' : musica.id_artista,
                        'id_musica' : musica.id_musica,
                        'nome_artista' : musica.nome_artista,
                        'nome_musica' : musica.nome_musica,
                        'popularidade' : musica.popularidade,
                        'acordes' : musica.acordes,
                        'genero' : musica.genero,
                        'url' : musica.url,
                        'diferenca' : list(diff),
                        'intersecao' : list(inter)
                }

                similares.append(similar)

    # ordenados por menor diferença, maior interseção e maior popularidade.
    return sorted(similares, key=lambda x: (len(x['diferenca']), -len(x['intersecao'])))

## Filtra a coleção de músicas por gênero.
def apply_filtro(musicas, generos_key):
    # filtra para melhor desempenho
    collection = []
    for genero in generos_key:
        if genero in generos:
            collection += genero_musicas[genero]
    return collection

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run(debug=True)

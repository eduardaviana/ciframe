# coding: utf-8
"""Valida o matcher do Passo 2 (sequências customizadas).

O que é verificado:
1. Regressão: para cada uma das 6 sequências originais, o conjunto de músicas
   retornado por `musica_compatível_com_sequencia` é idêntico ao conjunto
   marcado na coluna `SEQ_FAMOSA` do dataset.
2. Regras do algoritmo: ordem importa, precisa ser contígua e os acordes
   distintos da música precisam ser subconjunto dos acordes da sequência.
   Também cobre sequência vazia, cifra vazia, sequência maior que a cifra e
   acordes repetidos.

Testes de rotas ficam em `tests/test_passo3_routes.py` (Passo 3).

Uso (a partir da raiz do repositório):
    py tests/test_passo2_matcher.py
"""

import builtins
import os
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

# Isola o banco do teste: o matcher não precisa do catálogo real.
_TMP_DIR = tempfile.TemporaryDirectory(prefix='deciframe_passo2_')
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

from musica import Musica  # noqa: E402

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


def testar_regressao_seq_famosa():
    print('\n[1] Regressão contra SEQ_FAMOSA (6 sequências originais)')
    for indice, (nome, acordes) in enumerate(SEQUENCIAS):
        esperadas = {
            m.id_unico_musica
            for m in main.musicas.values()
            if str(indice) in m.seqs_famosas
        }
        obtidas = {
            m.id_unico_musica
            for m in main.musicas.values()
            if main.musica_compatível_com_sequencia(m, acordes)
        }
        so_esperadas = esperadas - obtidas
        so_obtidas = obtidas - esperadas
        print(
            '  %d %-8s esperadas=%d obtidas=%d so_esperadas=%d so_obtidas=%d'
            % (indice, nome, len(esperadas), len(obtidas), len(so_esperadas), len(so_obtidas))
        )
        if so_esperadas:
            print('    exemplos que faltaram:', sorted(so_esperadas)[:5])
        if so_obtidas:
            print('    exemplos a mais:', sorted(so_obtidas)[:5])
        checar(esperadas == obtidas, 'sequência %s idêntica ao SEQ_FAMOSA' % nome)


def testar_regras_do_algoritmo():
    print('\n[2] Regras do algoritmo (casos sintéticos)')
    c_g_am_f = Musica('a', 'Artista', '1', 'Musica', 'Rock', 1, [], 'C',
                      ['C', 'G', 'Am', 'F'])

    checar(
        main.musica_compatível_com_sequencia(c_g_am_f, ['C', 'G', 'Am', 'F']),
        'aceita sequência que aparece na ordem e cobre todos os acordes da música',
    )
    checar(
        not main.musica_compatível_com_sequencia(c_g_am_f, ['G', 'C', 'Am', 'F']),
        'rejeita quando a ordem é diferente',
    )
    checar(
        not main.musica_compatível_com_sequencia(c_g_am_f, ['C', 'G', 'F', 'Am']),
        'rejeita quando a sequência não é contígua',
    )
    checar(
        not main.musica_compatível_com_sequencia(c_g_am_f, ['C', 'G', 'Am']),
        'rejeita quando a música tem acorde fora da sequência (F)',
    )
    checar(
        not main.musica_compatível_com_sequencia(c_g_am_f, []),
        'rejeita sequência vazia',
    )

    musica_sem_cifra = Musica('b', 'Artista', '2', 'Sem cifra', 'Rock', 1, [], 'C', [])
    checar(
        not main.musica_compatível_com_sequencia(musica_sem_cifra, ['C', 'G']),
        'rejeita música com cifra vazia',
    )

    musica_curta = Musica('c', 'Artista', '3', 'Curta', 'Rock', 1, [], 'C',
                         ['C', 'G'])
    checar(
        not main.musica_compatível_com_sequencia(musica_curta, ['C', 'G', 'Am']),
        'rejeita sequência maior que a cifra da música',
    )

    musica_com_repeticao = Musica('d', 'Artista', '4', 'Repetida', 'Rock', 1, [], 'C',
                                  ['C', 'G', 'C'])
    checar(
        main.musica_compatível_com_sequencia(
            musica_com_repeticao, ['C', 'G', 'C']),
        'aceita sequência com repetição quando a ordem da cifra é respeitada',
    )
    checar(
        not main.musica_compatível_com_sequencia(
            musica_com_repeticao, ['C', 'C', 'G']),
        'não colapsa acordes repetidos da sequência',
    )


if __name__ == '__main__':
    testar_regressao_seq_famosa()
    testar_regras_do_algoritmo()

    print('\n' + '=' * 60)
    if falhas:
        print('%d verificação(ões) falharam.' % len(falhas))
        sys.exit(1)
    print('PASSO 2 VALIDADO COM SUCESSO!')

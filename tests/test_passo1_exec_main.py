# coding: utf-8
"""Valida o Passo 1 usando um banco SQLite temporário.

Cobre:
1. Criação do diretório e do arquivo do banco.
2. Criação da tabela `sequencias` com as restrições esperadas.
3. Seed das 6 sequências originais.
4. Persistência de uma sequência customizada entre duas inicializações.
5. Ausência de duplicatas.

O banco real em `data/db/sequencias.db` não é tocado.

Uso (a partir da raiz do repositório):
    py tests/test_passo1_exec_main.py
"""

import os
import sqlite3
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEQUENCIAS = [
    ('BmGDA', 'Bm;G;D;A'),
    ('CGAmF', 'C;G;Am;F'),
    ('EmG', 'Em;G'),
    ('CA7DmG7', 'C;A7;Dm;G7'),
    ('GmF', 'Gm;F'),
    ('CC7FFm', 'C;C7;F;Fm'),
]

falhas = []


def checar(condicao, mensagem):
    if condicao:
        print('  OK:', mensagem)
    else:
        print('  FALHA:', mensagem)
        falhas.append(mensagem)


def inicializar_com_banco_temporario(db_path):
    env = os.environ.copy()
    env['SEQUENCIAS_DB_PATH'] = db_path
    env['PYTHONUTF8'] = '1'

    resultado = subprocess.run(
        [sys.executable, '-c', 'import main'],
        cwd=BASE_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if resultado.returncode != 0:
        print('  Saída do processo:')
        print(resultado.stdout)
        print(resultado.stderr)
        return False
    return True


def abrir_banco(db_path):
    return sqlite3.connect(db_path)


def testar_passo1():
    print('Testando Passo 1 com banco temporário (sem tocar no banco real)')

    with tempfile.TemporaryDirectory(prefix='deciframe_passo1_') as tmp_dir:
        db_path = os.path.join(tmp_dir, 'banco', 'sequencias.db')

        checar(not os.path.exists(db_path),
               'banco temporário começa inexistente')
        checar(inicializar_com_banco_temporario(db_path),
               'importação do main.py executa sem erro')
        checar(os.path.exists(db_path),
               'banco foi criado no caminho de SEQUENCIAS_DB_PATH')
        checar(os.path.isdir(os.path.dirname(db_path)),
               'diretório do banco foi criado automaticamente')

        conn = abrir_banco(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT sql FROM sqlite_master "
                "WHERE type = 'table' AND name = 'sequencias'"
            )
            schema = cur.fetchone()

            checar(schema is not None, 'tabela sequencias existe')
            if schema:
                print('  Schema:', schema[0])
                checar('UNIQUE' in schema[0].upper(),
                       'coluna sequencia tem restrição UNIQUE')

            cur.execute('SELECT sequencia, acordes FROM sequencias ORDER BY id')
            rows = cur.fetchall()
            print('  Total de sequências:', len(rows))
            for row in rows:
                print('    -', row[0], '|', row[1])

            keys = [row[0] for row in rows]
            for nome, acordes in SEQUENCIAS:
                checar(nome in keys,
                       'sequência original %s foi seedada' % nome)
                item = next((row for row in rows if row[0] == nome), None)
                checar(item is not None and item[1] == acordes,
                       'sequência original %s tem os acordes esperados' % nome)

            checar(len(rows) == len(SEQUENCIAS),
                   'banco novo contém exatamente as 6 originais')

            cur.execute(
                'SELECT sequencia, COUNT(*) FROM sequencias '
                'GROUP BY sequencia HAVING COUNT(*) > 1'
            )
            checar(cur.fetchall() == [], 'não há sequências duplicadas')

            cur.execute(
                'INSERT INTO sequencias (sequencia, acordes) VALUES (?, ?)',
                ('TestePasso1', 'C;G')
            )
            conn.commit()
        finally:
            conn.close()

        checar(inicializar_com_banco_temporario(db_path),
               'segunda inicialização executa sem erro')

        conn = abrir_banco(db_path)
        try:
            cur = conn.cursor()
            cur.execute('SELECT sequencia, acordes FROM sequencias ORDER BY id')
            rows_apos_restart = cur.fetchall()
            keys_apos_restart = [row[0] for row in rows_apos_restart]

            checar('TestePasso1' in keys_apos_restart,
                   'sequência customizada persiste após reinicialização')
            checar(all(nome in keys_apos_restart for nome, _ in SEQUENCIAS),
                   'as 6 originais continuam presentes após reinicialização')
            checar(len(rows_apos_restart) == len(SEQUENCIAS) + 1,
                   'reinicialização não duplica as sequências')
        finally:
            conn.close()


if __name__ == '__main__':
    testar_passo1()

    print('\n' + '=' * 60)
    if falhas:
        print('%d verificação(ões) falharam.' % len(falhas))
        sys.exit(1)
    print('PASSO 1 VALIDADO COM SUCESSO!')

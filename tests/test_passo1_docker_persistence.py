# coding: utf-8
"""Valida a persistência do catálogo em um volume Docker.

Fluxo:
1. Constrói a imagem.
2. Sobe um container com volume nomeado.
3. Cadastra uma sequência via POST /sequencias.
4. Remove e recria o container com o mesmo volume.
5. Confirma que a sequência continua no catálogo.
6. Sobe um container sem volume e confirma que a sequência desapareceu.

Se o Docker não estiver disponível, o teste é ignorado (SKIP), sem falhar.

Uso (a partir da raiz do repositório):
    py tests/test_passo1_docker_persistence.py
"""

import json
import os
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE = 'ciframe:test-persistencia'
SUFIXO = str(os.getpid())
CONTAINER = 'deciframe-passo1-' + SUFIXO
CONTAINER_SEM_VOLUME = CONTAINER + '-sem-volume'
VOLUME = 'deciframe-passo1-volume-' + SUFIXO
TEST_KEY = 'CEmFG'
ORIGINAIS = {
    'BmGDA', 'CGAmF', 'EmG', 'CA7DmG7', 'GmF', 'CC7FFm',
}

falhas = []


def checar(condicao, mensagem):
    if condicao:
        print('  OK:', mensagem)
    else:
        print('  FALHA:', mensagem)
        falhas.append(mensagem)


def docker(*args):
    return subprocess.run(
        ['docker'] + list(args),
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


def docker_disponivel():
    try:
        return docker('info').returncode == 0
    except FileNotFoundError:
        return False


def porta_livre():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]
    finally:
        sock.close()


def subir_container(nome, porta, com_volume):
    args = [
        'run', '-d', '--name', nome,
        '-p', '%d:8080' % porta,
    ]
    if com_volume:
        args.extend(['-v', '%s:/app/data/db' % VOLUME])
    args.append(IMAGE)

    resultado = docker(*args)
    if resultado.returncode != 0:
        print(resultado.stdout)
        print(resultado.stderr)
        return False
    return True


def aguardar_catalogo(porta, tentativas=60):
    url = 'http://127.0.0.1:%d/sequencias' % porta
    for _ in range(tentativas):
        try:
            with urlopen(url, timeout=2) as resposta:
                return json.loads(resposta.read().decode('utf-8'))
        except (URLError, HTTPError, OSError):
            time.sleep(1)
    return None


def catalogo_atual(porta):
    with urlopen('http://127.0.0.1:%d/sequencias' % porta, timeout=5) as resposta:
        return json.loads(resposta.read().decode('utf-8'))


def cadastrar(porta, acordes):
    dados = json.dumps({'sequencia': acordes}).encode('utf-8')
    request = Request(
        'http://127.0.0.1:%d/sequencias' % porta,
        data=dados,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urlopen(request, timeout=5) as resposta:
        return resposta.status, json.loads(resposta.read().decode('utf-8'))


def mostrar_logs(nome):
    print('  Logs do container %s:' % nome)
    resultado = docker('logs', nome)
    print(resultado.stdout)
    print(resultado.stderr)


def limpar():
    docker('rm', '-f', CONTAINER)
    docker('rm', '-f', CONTAINER_SEM_VOLUME)
    docker('volume', 'rm', VOLUME)
    docker('rmi', '-f', IMAGE)


def testar_persistencia_docker():
    print('Testando persistência Docker (Passo 1)')

    if not docker_disponivel():
        print('  SKIP: Docker não está disponível neste ambiente.')
        return 2

    porta_com_volume = porta_livre()
    porta_apos_recriar = porta_livre()
    porta_sem_volume = porta_livre()

    try:
        print('  Construindo imagem...')
        build = docker('build', '-t', IMAGE, '.')
        if build.returncode != 0:
            print(build.stdout)
            print(build.stderr)
            return 1

        volume = docker('volume', 'create', VOLUME)
        if volume.returncode != 0:
            print(volume.stdout)
            print(volume.stderr)
            return 1

        checar(
            subir_container(CONTAINER, porta_com_volume, com_volume=True),
            'container com volume sobe',
        )
        catalogo = aguardar_catalogo(porta_com_volume)
        if catalogo is None:
            mostrar_logs(CONTAINER)
            return 1

        chaves = {item['sequencia'] for item in catalogo}
        checar(chaves == ORIGINAIS,
               'container novo com volume contém apenas as 6 originais')

        status, cadastrada = cadastrar(
            porta_com_volume, ['C', 'Em', 'F', 'G'])
        checar(status == 200, 'POST /sequencias responde 200 no container')
        checar(cadastrada.get('sequencia') == TEST_KEY,
               'POST /sequencias retorna a sequência de teste')

        chaves = {item['sequencia'] for item in catalogo_atual(porta_com_volume)}
        checar(TEST_KEY in chaves,
               'sequência aparece no catálogo antes da recriação')

        docker('rm', '-f', CONTAINER)
        checar(
            subir_container(CONTAINER, porta_apos_recriar, com_volume=True),
            'container é recriado com o mesmo volume',
        )
        catalogo = aguardar_catalogo(porta_apos_recriar)
        if catalogo is None:
            mostrar_logs(CONTAINER)
            return 1

        chaves = {item['sequencia'] for item in catalogo}
        checar(TEST_KEY in chaves,
               'sequência persiste após remover e recriar o container')
        checar(ORIGINAIS.issubset(chaves),
               'as 6 originais continuam presentes após a recriação')

        docker('rm', '-f', CONTAINER)
        checar(
            subir_container(CONTAINER_SEM_VOLUME, porta_sem_volume, com_volume=False),
            'container sem volume sobe',
        )
        catalogo = aguardar_catalogo(porta_sem_volume)
        if catalogo is None:
            mostrar_logs(CONTAINER_SEM_VOLUME)
            return 1

        chaves = {item['sequencia'] for item in catalogo}
        checar(TEST_KEY not in chaves,
               'sequência não aparece no container sem volume')
        checar(chaves == ORIGINAIS,
               'container sem volume recria apenas as 6 originais')
    finally:
        limpar()

    return 0


if __name__ == '__main__':
    codigo = testar_persistencia_docker()

    print('\n' + '=' * 60)
    if codigo == 2 and not falhas:
        print('PASSO 1 (PERSISTÊNCIA DOCKER) IGNORADO: Docker indisponível.')
        sys.exit(0)
    if codigo != 0 or falhas:
        if falhas:
            print('%d verificação(ões) falharam.' % len(falhas))
        sys.exit(1)
    print('PASSO 1 (PERSISTÊNCIA DOCKER) VALIDADO COM SUCESSO!')

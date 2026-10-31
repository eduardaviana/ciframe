#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste da hipótese (gerado separadamente, sem modificar código existente)

Hipótese:
"O que irá definir se a sequência X aparece na música Y é verificar se a sequência completa digitada, em ordem, pelo usuário está contida pelo menos uma vez na lista de cifras que a música possui e se o conjunto de acordes das cifra é composto apenas pelos acordes da sequencia digitada. A música possui tanto lista de acordes quanto lista de cifras, mas a cifra está ordenada como vem na música, e os acordes são só todos os acordes distintos presentes na música. Logo, por a ordem da sequência importar, a ordem dos acordes importa para analisar se a sequencia esta presente pelo menos uma vez na música."

Sequências usadas: mesmas definidas em main.py:40-45
0 -> ['Bm','G','D','A'] (BmGDA)
1 -> ['C','G','Am','F'] (CGAmF)
2 -> ['Em','G'] (EmG)
3 -> ['C','A7','Dm','G7'] (CA7DmG7)
4 -> ['Gm','F'] (GmF)
5 -> ['C','C7','F','Fm'] (CC7FFm)

Compara com ground truth: coluna SEQ_FAMOSA (dividida por ';') do data/top/dataset_final.csv
"""

import csv
import sys
import os

# Forçar encoding correto
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'data', 'top', 'dataset_final.csv')
    
    # Sequências famosas conforme main.py:40-45
    seqs_map = {
        '0': ['Bm','G','D','A'],
        '1': ['C','G','Am','F'],
        '2': ['Em','G'],
        '3': ['C','A7','Dm','G7'],
        '4': ['Gm','F'],
        '5': ['C','C7','F','Fm'],
    }
    seq_names = {
        '0': 'BmGDA',
        '1': 'CGAmF',
        '2': 'EmG',
        '3': 'CA7DmG7',
        '4': 'GmF',
        '5': 'CC7FFm',
    }
    
    print('=== TESTE DA HIPÓTESE (sem modificar código) ===')
    print('Sequências famosas (main.py:40-45):')
    for k, v in seqs_map.items():
        print(f'  {k} -> {v} ({seq_names[k]})')
    print()
    print('Dataset:', csv_path)
    print()
    
    # Tentar diferentes encodings
    encodings = ['latin-1', 'utf-8', 'cp1252']
    f = None
    for enc in encodings:
        try:
            f = open(csv_path, encoding=enc)
            # testar leitura
            reader_test = csv.reader(f)
            next(reader_test)
            f.seek(0)
            break
        except Exception:
            if f:
                f.close()
            f = None
    
    if f is None:
        print('ERRO: Não foi possível abrir o arquivo CSV')
        return
    
    try:
        reader = csv.reader(f)
        # pular cabeçalho
        header = next(reader)
        
        # Coletar resultados por linha
        resultados_linhas = []
        
        for row_idx, row in enumerate(reader):
            if len(row) < 9:
                continue
            # SEQ_FAMOSA é coluna 7 (index 7)
            seq_famosa_col = row[7] if len(row) > 7 else 'NA'
            # CIFRA é coluna 8 (index 8)
            cifra_col = row[8] if len(row) > 8 else ''
            
            # Ground truth: tags na coluna SEQ_FAMOSA
            if seq_famosa_col == 'NA' or seq_famosa_col.strip() == '':
                tags_gt = []
            else:
                if ';' in seq_famosa_col:
                    tags_gt = [t.strip() for t in seq_famosa_col.split(';') if t.strip() != '']
                else:
                    tags_gt = [seq_famosa_col.strip()] if seq_famosa_col.strip() != '' else []
            
            # Processar cifra: lista ordenada
            if cifra_col.strip() == '':
                cifra_lista = []
            else:
                if ';' in cifra_col:
                    cifra_lista = [x.strip() for x in cifra_col.split(';') if x.strip() != '']
                else:
                    cifra_lista = [x.strip() for x in cifra_col.split() if x.strip() != '']
            
            # Conjunto distinto
            cifra_distintos = set(cifra_lista)
            
            # Aplicar hipótese para cada sequência
            tags_algo = []
            for seq_id, seq_list in seqs_map.items():
                seq_distintos = set(seq_list)
                # Condição 1: sequência completa em ordem aparece pelo menos uma vez contígua
                aparece_contigua = False
                if len(cifra_lista) >= len(seq_list):
                    for j in range(len(cifra_lista) - len(seq_list) + 1):
                        match = True
                        for k in range(len(seq_list)):
                            if cifra_lista[j + k] != seq_list[k]:
                                match = False
                                break
                        if match:
                            aparece_contigua = True
                            break
                # Condição 2: conjunto distinto da cifra composto apenas pelos acordes da sequência
                apenas_acordes_sequencia = cifra_distintos.issubset(seq_distintos)
                
                if aparece_contigua and apenas_acordes_sequencia:
                    tags_algo.append(seq_id)
            
            # Ordenar tags
            tags_gt_sorted = sorted(list(set(tags_gt)))
            tags_algo_sorted = sorted(list(set(tags_algo)))
            
            resultados_linhas.append({
                'idx': row_idx,
                'artist': row[2] if len(row) > 2 else '',
                'song': row[3] if len(row) > 3 else '',
                'gt': tags_gt_sorted,
                'algo': tags_algo_sorted,
                'igual': tags_gt_sorted == tags_algo_sorted
            })
        
        # Calcular totais por sequência
        for seq_id in ['0','1','2','3','4','5']:
            gt_count = sum(1 for r in resultados_linhas if seq_id in r['gt'])
            algo_count = sum(1 for r in resultados_linhas if seq_id in r['algo'])
            iguais = sum(1 for r in resultados_linhas if (seq_id in r['gt']) == (seq_id in r['algo']))
            apenas_gt = sum(1 for r in resultados_linhas if (seq_id in r['gt']) and (seq_id not in r['algo']))
            apenas_algo = sum(1 for r in resultados_linhas if (seq_id not in r['gt']) and (seq_id in r['algo']))
            diverg = apenas_gt + apenas_algo
            
            print(f'--- SEQ {seq_id} {seqs_map[seq_id]} ({seq_names[seq_id]}) ---')
            print(f'  Ground truth (SEQ_FAMOSA contains \'{seq_id}\'): {gt_count}')
            print(f'  Algoritmo (contiguo_na_ordem E distintos_cifra_subconjunto_sequencia): {algo_count}')
            print(f'  Iguais (interseção/mesmo conjunto): {iguais}')
            print(f'  Apenas no dataset (tag existe mas algoritmo não acha): {apenas_gt}')
            print(f'  Apenas no algoritmo (algoritmo acha mas tag não existe): {apenas_algo}')
            print(f'  Divergências (diferença entre conjuntos): {diverg}')
            print()
        
        # Totais gerais
        linhas_com_gt = sum(1 for r in resultados_linhas if len(r['gt']) > 0)
        linhas_com_algo = sum(1 for r in resultados_linhas if len(r['algo']) > 0)
        linhas_iguais = sum(1 for r in resultados_linhas if r['igual'])
        linhas_diverg = len(resultados_linhas) - linhas_iguais
        
        print('=== TOTAIS ===')
        print(f'  Ground truth total (linhas com qualquer seq famosa): {linhas_com_gt}')
        print(f'  Algoritmo total (qualquer seq famosa): {linhas_com_algo}')
        print(f'  Linhas com resultado IGUAL (mesmo conjunto de seqs detectadas): {linhas_iguais}')
        print(f'  Linhas com DIVERGÊNCIA: {linhas_diverg}')
        print()
        
        # Mostrar divergências se houver
        if linhas_diverg > 0:
            print('=== DIVERGÊNCIAS ===')
            for r in resultados_linhas:
                if not r['igual']:
                    print(f'  Linha {r["idx"]}: {r["artist"]} - {r["song"]}')
                    print(f'    GT: {r["gt"]} | ALGO: {r["algo"]}')
            print()
        else:
            print('=== RESULTADO ===')
            print('  TODAS AS LINHAS COM SEQUÊNCIAS FAMOSAS FORAM IGUAIS!')
            print()
        
    finally:
        f.close()

if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste: apenas se a sequência aparece pelo menos uma vez de forma contígua na cifra
Compara com ground truth: coluna SEQ_FAMOSA do data/top/dataset_final.csv
"""

import csv
import sys
import os

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'data', 'top', 'dataset_final.csv')
    
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
    
    print('=== TESTE: APENAS SEQUÊNCIA CONTÍGUA NA CIFRA ===')
    print('Sequências famosas (main.py:40-45):')
    for k, v in seqs_map.items():
        print(f'  {k} -> {v} ({seq_names[k]})')
    print()
    print('Dataset:', csv_path)
    print()
    
    encodings = ['latin-1', 'utf-8', 'cp1252']
    f = None
    for enc in encodings:
        try:
            f = open(csv_path, encoding=enc)
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
        header = next(reader)
        
        resultados_linhas = []
        for row_idx, row in enumerate(reader):
            if len(row) < 9:
                continue
            seq_famosa_col = row[7] if len(row) > 7 else 'NA'
            cifra_col = row[8] if len(row) > 8 else ''
            
            if seq_famosa_col == 'NA' or seq_famosa_col.strip() == '':
                tags_gt = []
            else:
                if ';' in seq_famosa_col:
                    tags_gt = [t.strip() for t in seq_famosa_col.split(';') if t.strip() != '']
                else:
                    tags_gt = [seq_famosa_col.strip()] if seq_famosa_col.strip() != '' else []
            
            if cifra_col.strip() == '':
                cifra_lista = []
            else:
                if ';' in cifra_col:
                    cifra_lista = [x.strip() for x in cifra_col.split(';') if x.strip() != '']
                else:
                    cifra_lista = [x.strip() for x in cifra_col.split() if x.strip() != '']
            
            tags_algo = []
            for seq_id, seq_list in seqs_map.items():
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
                if aparece_contigua:
                    tags_algo.append(seq_id)
            
            tags_gt_sorted = sorted(list(set(tags_gt)))
            tags_algo_sorted = sorted(list(set(tags_algo)))
            resultados_linhas.append({
                'gt': tags_gt_sorted,
                'algo': tags_algo_sorted,
                'igual': tags_gt_sorted == tags_algo_sorted
            })
        
        for seq_id in ['0','1','2','3','4','5']:
            gt_count = sum(1 for r in resultados_linhas if seq_id in r['gt'])
            algo_count = sum(1 for r in resultados_linhas if seq_id in r['algo'])
            apenas_gt = sum(1 for r in resultados_linhas if (seq_id in r['gt']) and (seq_id not in r['algo']))
            apenas_algo = sum(1 for r in resultados_linhas if (seq_id not in r['gt']) and (seq_id in r['algo']))
            diverg = apenas_gt + apenas_algo
            print(f'--- SEQ {seq_id} {seqs_map[seq_id]} ({seq_names[seq_id]}) ---')
            print(f'  Ground truth: {gt_count}')
            print(f'  Apenas contígua: {algo_count}')
            print(f'  Apenas no dataset: {apenas_gt}')
            print(f'  Apenas no algoritmo: {apenas_algo}')
            print(f'  Divergências: {diverg}')
            print()
        
        linhas_com_gt = sum(1 for r in resultados_linhas if len(r['gt']) > 0)
        linhas_com_algo = sum(1 for r in resultados_linhas if len(r['algo']) > 0)
        linhas_iguais = sum(1 for r in resultados_linhas if r['igual'])
        print('=== TOTAIS ===')
        print(f'  Ground truth total (linhas com qualquer seq famosa): {linhas_com_gt}')
        print(f'  Apenas contígua total: {linhas_com_algo}')
        print(f'  Linhas com resultado IGUAL: {linhas_iguais}')
        print(f'  Linhas com DIVERGÊNCIA: {len(resultados_linhas) - linhas_iguais}')
        print()
    finally:
        f.close()

if __name__ == '__main__':
    main()

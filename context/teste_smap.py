#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para verificar se o arquivo InnovationBox.smap é carregado corretamente
"""
import json
import os

print("=" * 70)
print("TESTE DE LEITURA DO ARQUIVO InnovationBox.smap")
print("=" * 70)

arquivo = 'InnovationBox.smap'

if not os.path.exists(arquivo):
    print(f"\n❌ ERRO: Arquivo '{arquivo}' não encontrado!")
    print(f"   Diretório atual: {os.getcwd()}")
    exit(1)

print(f"\n✅ Arquivo encontrado: {arquivo}")
print(f"   Tamanho: {os.path.getsize(arquivo) / 1024:.2f} KB")

# Carrega o arquivo
with open(arquivo, 'r', encoding='utf-8') as f:
    dados = json.load(f)

print("\n" + "=" * 70)
print("ESTRUTURA DO ARQUIVO")
print("=" * 70)

# Header
if 'header' in dados:
    header = dados['header']
    print("\n📋 HEADER:")
    print(f"   Tipo de mapa: {header.get('mapType')}")
    print(f"   Nome do mapa: {header.get('mapName')}")
    print(f"   Resolução: {header.get('resolution')}")
    print(f"   Versão: {header.get('version')}")
    
    if 'minPos' in header and 'maxPos' in header:
        print(f"\n📏 LIMITES DO MAPA:")
        print(f"   X: {header['minPos']['x']:.3f} a {header['maxPos']['x']:.3f}")
        print(f"   Y: {header['minPos']['y']:.3f} a {header['maxPos']['y']:.3f}")

# Listas de dados
print(f"\n📊 DADOS DISPONÍVEIS:")
for chave in dados.keys():
    if chave != 'header':
        if isinstance(dados[chave], list):
            print(f"   {chave}: {len(dados[chave])} itens")
        else:
            print(f"   {chave}: {type(dados[chave]).__name__}")

# Landmarks
if 'landmarkList' in dados and len(dados['landmarkList']) > 0:
    print(f"\n🎯 LANDMARKS ({len(dados['landmarkList'])} encontrados):")
    for i, lm in enumerate(dados['landmarkList'][:5]):  # Mostra os 5 primeiros
        print(f"   {i+1}. {lm}")
    if len(dados['landmarkList']) > 5:
        print(f"   ... e mais {len(dados['landmarkList']) - 5} landmarks")
else:
    print("\n⚠️  Nenhum landmark encontrado no campo 'landmarkList'")

# Linhas do mapa
if 'lineList' in dados and len(dados['lineList']) > 0:
    print(f"\n📐 LINHAS DO MAPA ({len(dados['lineList'])} encontradas):")
    for i, linha in enumerate(dados['lineList'][:3]):  # Mostra as 3 primeiras
        print(f"   {i+1}. {linha}")
    if len(dados['lineList']) > 3:
        print(f"   ... e mais {len(dados['lineList']) - 3} linhas")
else:
    print("\n⚠️  Nenhuma linha encontrada no campo 'lineList'")

# Posição do robô
if 'robotPos' in dados:
    robot_pos = dados['robotPos']
    print(f"\n🤖 POSIÇÃO INICIAL DO ROBÔ:")
    print(f"   {robot_pos}")
else:
    print("\n⚠️  Posição do robô não encontrada no campo 'robotPos'")

# Pontos normais (mapa de navegação)
if 'normalPosList' in dados:
    print(f"\n🗺️  PONTOS DO MAPA DE NAVEGAÇÃO: {len(dados['normalPosList'])} pontos")
    print(f"   (Estes são os pontos navegáveis do mapa)")

print("\n" + "=" * 70)
print("TESTE CONCLUÍDO")
print("=" * 70)

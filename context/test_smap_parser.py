import json

# Testa o parsing do arquivo .smap
arquivo = 'InnovationBox.smap'

print("Testando parser do .smap...")
try:
    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read().strip()
        if '\n' in conteudo:
            conteudo = conteudo.split('\n')[0]
        dados = json.loads(conteudo)
    
    print("\n✅ JSON carregado com sucesso!")
    print(f"Chaves principais: {list(dados.keys())}")
    
    if 'header' in dados:
        header = dados['header']
        print(f"\n📍 Header encontrado:")
        print(f"  Tipo de mapa: {header.get('mapType')}")
        print(f"  Nome: {header.get('mapName')}")
        print(f"  Resolução: {header.get('resolution')}")
        print(f"  Versão: {header.get('version')}")
        
        min_pos = header.get('minPos', {})
        max_pos = header.get('maxPos', {})
        print(f"  MinPos: {min_pos}")
        print(f"  MaxPos: {max_pos}")
    
    if 'normalPosList' in dados:
        print(f"\n📊 normalPosList: {len(dados['normalPosList'])} pontos")
        if len(dados['normalPosList']) > 0:
            print(f"  Primeiro ponto: {dados['normalPosList'][0]}")
    
    if 'normalLineList' in dados:
        print(f"\n📏 normalLineList: {len(dados['normalLineList'])} linhas")
    
    if 'advancedPointList' in dados:
        print(f"\n📌 advancedPointList: {len(dados['advancedPointList'])} pontos avançados")
        if len(dados['advancedPointList']) > 0:
            print(f"  Primeiro ponto: {dados['advancedPointList'][0]}")
    
    if 'advancedLineList' in dados:
        print(f"\n📐 advancedLineList: {len(dados['advancedLineList'])} linhas avançadas")
    
    if 'advancedCurveList' in dados:
        print(f"\n🔄 advancedCurveList: {len(dados['advancedCurveList'])} curvas")
    
    if 'advancedAreaList' in dados:
        print(f"\n🗺️  advancedAreaList: {len(dados['advancedAreaList'])} áreas")
        if len(dados['advancedAreaList']) > 0:
            area = dados['advancedAreaList'][0]
            print(f"  Primeira área: className={area.get('className')}, instanceName={area.get('instanceName')}")

except FileNotFoundError:
    print(f"❌ Arquivo não encontrado: {arquivo}")
except json.JSONDecodeError as e:
    print(f"❌ Erro ao decodificar JSON: {e}")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Teste concluído!")

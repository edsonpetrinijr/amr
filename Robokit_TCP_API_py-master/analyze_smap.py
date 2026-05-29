import json

# Analisa o arquivo .smap
with open('InnovationBox.smap', 'r') as f:
    data = json.load(f)

print("=" * 60)
print("ANÁLISE DO ARQUIVO InnovationBox.smap")
print("=" * 60)

print("\n1. HEADER:")
print(json.dumps(data['header'], indent=2))

print("\n2. CHAVES PRINCIPAIS:")
for key in data.keys():
    if isinstance(data[key], list):
        print(f"  - {key}: {len(data[key])} items")
    else:
        print(f"  - {key}: {type(data[key])}")

# Verifica se tem posição do robô
if 'robotPos' in data:
    print("\n3. POSIÇÃO INICIAL DO ROBÔ:")
    print(f"  {json.dumps(data['robotPos'], indent=2)}")

# Verifica landmarks
if 'landmarkList' in data:
    print("\n4. LANDMARKS:")
    for lm in data['landmarkList'][:5]:  # Mostra apenas os 5 primeiros
        print(f"  {json.dumps(lm)}")
    if len(data['landmarkList']) > 5:
        print(f"  ... e mais {len(data['landmarkList']) - 5} landmarks")

# Verifica linhas do mapa
if 'lineList' in data:
    print("\n5. LINHAS DO MAPA (paredes/obstáculos):")
    for line in data['lineList'][:3]:  # Mostra apenas as 3 primeiras
        print(f"  {json.dumps(line)}")
    if len(data['lineList']) > 3:
        print(f"  ... e mais {len(data['lineList']) - 3} linhas")

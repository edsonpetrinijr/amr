# 📋 COMO USAR O ARQUIVO InnovationBox.smap COM O VISUALIZADOR

## 🎯 Sobre o arquivo .smap

O arquivo `InnovationBox.smap` contém todas as informações do mapa do RoboShop Pro:
- **Landmarks** (pontos de interesse/destinos)
- **Paredes e obstáculos** (lineList)
- **Pontos navegáveis** (normalPosList)
- **Posição inicial do robô** (robotPos, se disponível)
- **Limites do mapa** (minPos, maxPos)

## ✅ Modificações feitas no visualizador_auto.py

O arquivo `visualizador_auto.py` foi modificado para:

1. **Carregar automaticamente o arquivo .smap local**
   - Busca primeiro por arquivos locais: `InnovationBox.smap`, `map.smap`, `mapa.smap`
   - Se não encontrar, tenta baixar do robô via API

2. **Extrair todas as informações do mapa**
   - Landmarks (landmarkList)
   - Linhas/paredes (lineList)
   - Posição inicial do robô (robotPos)
   - Limites do mapa (header.minPos e header.maxPos)

3. **Ajustar automaticamente a visualização**
   - Os limites do gráfico são ajustados conforme o mapa
   - A posição inicial do robô é carregada do arquivo

## 🚀 Como usar

### 1. Certifique-se de que o arquivo InnovationBox.smap está na mesma pasta do visualizador

```
Robokit_TCP_API_py-master/
├── InnovationBox.smap          ← Arquivo do mapa
├── visualizador_auto.py         ← Visualizador modificado
├── netprotocol/
└── ...
```

### 2. Execute o visualizador normalmente

```bash
python visualizador_auto.py
```

### 3. O visualizador irá:

✅ Detectar o arquivo InnovationBox.smap automaticamente
✅ Carregar todos os landmarks
✅ Carregar todas as paredes/obstáculos
✅ Carregar a posição inicial do robô (se disponível)
✅ Ajustar os limites da visualização automaticamente

## 🧪 Testando o carregamento do arquivo

Para verificar se o arquivo .smap está sendo lido corretamente, execute:

```bash
python teste_smap.py
```

Este script irá mostrar:
- Informações do header (nome, limites, resolução)
- Número de landmarks encontrados
- Número de linhas/paredes encontradas
- Posição inicial do robô (se disponível)
- Primeiros itens de cada lista

## 📊 Estrutura do arquivo InnovationBox.smap

```json
{
  "header": {
    "mapType": "2D-Map",
    "mapName": "InnovationBox",
    "minPos": {"x": -1.607, "y": -0.934},
    "maxPos": {"x": 2.765, "y": 6.35},
    "resolution": 0.02,
    "version": "1.0.6"
  },
  "normalPosList": [
    {"x": -1.607, "y": 0.532},
    ...
  ],
  "landmarkList": [
    {"id": "LM1", "x": 0.0, "y": 3.0},
    ...
  ],
  "lineList": [
    {
      "startPos": {"x": -1.5, "y": 0.0},
      "endPos": {"x": -1.5, "y": 6.0}
    },
    ...
  ],
  "robotPos": {
    "x": 0.0,
    "y": 0.0,
    "theta": 0.0
  }
}
```

## 🔧 Configuração manual (se necessário)

Se você quiser usar um arquivo .smap com outro nome, edite a lista `arquivos_locais` no método `buscar_mapa_landmarks()`:

```python
arquivos_locais = ['InnovationBox.smap', 'MeuMapa.smap', 'map.smap']
```

## ⚠️ Solução de problemas

### O visualizador não encontra o arquivo .smap

- Verifique se o arquivo está na mesma pasta do visualizador_auto.py
- Execute `python teste_smap.py` para verificar se o arquivo é válido
- Verifique se o nome do arquivo está correto (case-sensitive no Linux)

### O mapa aparece vazio

- Execute `python teste_smap.py` para verificar o conteúdo
- O arquivo pode não ter `landmarkList` ou `lineList`
- Verifique se o arquivo é um JSON válido

### A posição do robô não é carregada

- Nem todos os arquivos .smap têm o campo `robotPos`
- Neste caso, a posição será atualizada automaticamente quando o robô se conectar

## 📝 Notas

- O arquivo .smap é um arquivo JSON padrão
- Pode ser editado manualmente se necessário
- O visualizador dá prioridade ao arquivo local antes de tentar baixar do robô
- Se múltiplos arquivos .smap estiverem presentes, o primeiro encontrado será usado

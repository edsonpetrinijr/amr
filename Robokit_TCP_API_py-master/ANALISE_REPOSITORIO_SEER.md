# RESUMO DA ANÁLISE DO REPOSITÓRIO SMAP DA SEER ROBOTICS

## 🔍 O que encontramos

O repositório oficial da Seer (https://github.com/seer-robotics/smap) contém:

### 1. **message_map.proto** - Definição do formato
Arquivo Protobuf que define a estrutura dos mapas .smap

### 2. **Estrutura Principal** (`Message_Map`)
```
Message_Map {
  - header: Message_MapHeader (nome, tipo, limites, resolução)
  - normal_pos_list: pontos navegáveis (lista de Message_MapPos)
  - normal_line_list: linhas simples (lista de Message_MapLine)
  - advanced_point_list: pontos avançados (Message_AdvancedPoint)
  - advanced_line_list: linhas avançadas  
  - advanced_curve_list: curvas (Message_AdvancedCurve)
  - advanced_area_list: áreas (Message_AdvancedArea)
  - patrol_route_list: rotas de patrulha
  - rssi_pos_list: pontos RSSI
}
```

### 3. **Tipos Importantes**

**Message_MapPos:**
- `x`: double
- `y`: double

**Message_MapLine:**
- `start_pos`: Message_MapPos
- `end_pos`: Message_MapPos

**Message_AdvancedPoint (landmarks, estações):**
- `class_name`: string (tipo: "station", "waypoint", etc.)
- `instance_name`: string (nome único)
- `pos`: Message_MapPos
- `dir`: double (direção em radianos)
- `property`: lista de Message_MapProperty

**Message_AdvancedArea (áreas de detecção):**
- `class_name`: string
- `instance_name`: string  
- `pos_group`: lista de Message_MapPos (polígono)
- `property`: propriedades customizadas

### 4. **Formato do Arquivo**

O arquivo .smap é um JSON compacto (uma linha só) gerado a partir do Protobuf:

```json
{"header":{...},"normalPosList":[...],"advancedPointList":[...],...}
```

### 5. **Como Parsear (Exemplo C++)**

```cpp
std::fstream fs(mapPath, std::ios::in | std::ios::binary);
std::string line;
getline(fs, line);

rbk::protocol::Message_Map map_msg;
google::protobuf::util::JsonStringToMessage(line, &map_msg);
```

## ✅ O que vamos usar

1. **Header** para limites do mapa
2. **normalPosList** para pontos navegáveis  
3. **normalLineList** para paredes/obstáculos
4. **advancedPointList** para landmarks/estações
5. **advancedAreaList** para áreas especiais
6. **advancedCurveList** para rotas curvas

## 🔧 Correção necessária

O parser atual estava tentando acessar campos com nomes errados.
Campos corretos (camelCase):
- `minPos` e `maxPos` (não `min_pos`)
- `normalPosList` (não `normal_pos_list`)
- `advancedPointList` (não `advanced_point_list`)

Baseado no format do protocolo Protobuf da Seer Robotics.

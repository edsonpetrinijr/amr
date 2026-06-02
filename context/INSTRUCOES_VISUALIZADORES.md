# 🤖 VISUALIZADORES DO ROBOSHOP PRO - MODOS DE USO

## 📋 Arquivos Disponíveis

### 1. **visualizador_auto.py** (Principal - Automático)
Visualizador completo que funciona em **dois modos**:

#### Modo Online (padrão)
```bash
python visualizador_auto.py
```
- ✅ Conecta ao robô
- ✅ Busca mapa automaticamente
- ✅ Mostra posição em tempo real
- ✅ Rastreia trajetória
- ✅ Exibe status de navegação

#### Modo Offline (sem robô)
```bash
python visualizador_auto.py --offline
```
OU
```bash
python visualizador_auto.py -o
```
- 📴 Não conecta ao robô
- ✅ Carrega apenas arquivo .smap
- ✅ Visualiza mapa estático
- ✅ Mostra landmarks e paredes

---

### 2. **visualizador_offline.py** (Atalho Offline)
Atalho direto para modo offline:
```bash
python visualizador_offline.py
```
Equivalente a `python visualizador_auto.py --offline`

---

### 3. **visualizador_robo.py** (Manual)
Visualizador com configuração manual de landmarks:
```bash
python visualizador_robo.py
```
- ⚙️ Landmarks configurados manualmente no código
- 🔌 Requer conexão com robô

---

### 4. **visualizador_multi_robo.py**
Visualizador para múltiplos robôs:
```bash
python visualizador_multi_robo.py
```
- 🤖🤖 Suporte a vários robôs simultaneamente

---

## 📁 Arquivos .smap

Os visualizadores buscam automaticamente arquivos .smap nesta ordem:
1. `InnovationBox.smap` (seu arquivo atual)
2. `map.smap`
3. `mapa.smap`

### Formato do arquivo .smap
Baseado em Protocol Buffers da Seer Robotics. Campos principais:
- `header`: nome do mapa, limites (minPos, maxPos), resolução
- `normalPosList`: pontos navegáveis (array de {x, y})
- `normalLineList`: linhas/paredes (array com startPos e endPos)
- `advancedPointList`: landmarks/estações avançadas
- `advancedAreaList`: áreas especiais
- `advancedCurveList`: curvas de navegação

Documentação oficial: https://github.com/seer-robotics/smap

---

## 🔧 Correções Aplicadas

### Problema Resolvido
❌ **Erro anterior**: `'x'` ao carregar .smap  
✅ **Solução**: Parser agora valida tipos antes de acessar campos

### Mudanças
1. Validação segura de `minPos`/`maxPos`
2. Suporte a JSON em linha única (formato compacto)
3. Verificação de campos aninhados com `isinstance()`
4. Modo offline que não trava sem robô conectado

---

## 🚀 Uso Recomendado

### Para desenvolvimento/testes (sem robô físico):
```bash
python visualizador_offline.py
```

### Para operação com robô:
```bash
python visualizador_auto.py
```

### Para depuração de conexão:
```bash
python visualizador_auto.py --offline  # Testa só o mapa
python visualizador_auto.py            # Testa conexão + mapa
```

---

## 📊 Estrutura de Dados do .smap

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
    {"x": -1.605, "y": 0.347},
    ...
  ],
  "normalLineList": [
    {
      "startPos": {"x": 0.0, "y": 0.0},
      "endPos": {"x": 1.0, "y": 1.0}
    },
    ...
  ],
  "advancedPointList": [
    {
      "className": "station",
      "instanceName": "LM1",
      "pos": {"x": 0.0, "y": 3.0},
      "dir": 0.0
    },
    ...
  ]
}
```

---

## 🆘 Solução de Problemas

### "Erro ao carregar arquivo .smap: 'x'"
✅ **Resolvido** - Use a versão corrigida do visualizador_auto.py

### "Não foi possível conectar ao robô"
- Verifique o IP do robô em `ROBOT_IP` (linha 15)
- Teste modo offline: `python visualizador_offline.py`

### "Arquivo .smap não encontrado"
- Certifique-se que `InnovationBox.smap` está no mesmo diretório
- Use caminho absoluto se necessário

### "Mapa vazio/sem landmarks"
- Verifique estrutura do JSON com: `python test_smap_parser.py`
- Confirme que campos estão em camelCase (ex: `normalPosList`, não `normal_pos_list`)

---

## 📚 Referências

- Repositório oficial SMAP: https://github.com/seer-robotics/smap
- Protocol Buffers: https://developers.google.com/protocol-buffers
- Documentação Seer Robotics: Ver arquivo `robotkit-netprotocol-l-1.2.1.pdf`

---

**Última atualização**: 2026-05-28  
**Versão**: 2.0 (com suporte a modo offline)

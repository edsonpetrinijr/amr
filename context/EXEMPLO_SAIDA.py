#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EXEMPLO DE SAÍDA DO VISUALIZADOR COM InnovationBox.smap

Este é um exemplo do que você verá ao executar o visualizador_auto.py
com o arquivo InnovationBox.smap presente no diretório.
"""

print("""
================================================================================
🤖 VISUALIZADOR DO ROBO - COM CARREGAMENTO DO ARQUIVO .SMAP
================================================================================

🔍 Buscando configurações do robô...

  📂 Carregando arquivo local: InnovationBox.smap
  📍 Mapa: InnovationBox
  📏 Limites: X(-1.61 a 2.76), Y(-0.93 a 6.35)
  ✅ Carregados [X] landmarks
  ✅ Carregadas [Y] linhas do mapa
  ✅ Carregados [Z] pontos navegáveis
  🤖 Posição inicial do robô: X=0.00, Y=0.00, θ=0.00

  ✅ Mapa carregado com sucesso do arquivo local!

🔌 Conectando ao robô...
  ✅ Conectado à porta STATE (8082)

✅ Conexões estabelecidas!

  ℹ️  Desenhados [Z] pontos navegáveis (fundo)

================================================================================
🎨 VISUALIZAÇÃO
================================================================================

O mapa será exibido com:

┌─────────────────────────────────────────────────────┐
│ 🗺️  MAPA DO ROBOSHOP PRO - VISUALIZAÇÃO EM TEMPO REAL│
│                                                     │
│  ┌──────────────────────────────────────┐          │
│  │ • Pontos cinza (fundo) = área        │          │
│  │   navegável (normalPosList)          │          │
│  │                                      │          │
│  │ ╍╍ Linhas roxas = paredes/obstáculos │          │
│  │    (lineList)                        │          │
│  │                                      │          │
│  │ 🔴 LM1, LM2, ... = Landmarks         │          │
│  │    (landmarkList)                    │          │
│  │                                      │          │
│  │ 🔵 ▶ = Robô (posição e orientação)   │          │
│  │                                      │          │
│  │ 🟢 Linha verde = Trajetória percorrida│         │
│  │                                      │          │
│  │ ⭐ = Destino atual (se navegando)    │          │
│  │                                      │          │
│  └──────────────────────────────────────┘          │
│                                                     │
│ Informações em tempo real:                         │
│ ┌──────────────────────────────────────┐           │
│ │ Pos: X=1.23, Y=4.56, θ=90.00°       │           │
│ │ Vel: 0.50 m/s | 0.00 rad/s          │           │
│ │ Destino: LM5                         │           │
│ │ Status: NAVEGANDO                    │           │
│ └──────────────────────────────────────┘           │
└─────────────────────────────────────────────────────┘

================================================================================
🎯 O QUE VOCÊ VERÁ
================================================================================

1. FUNDO CINZA (pontos muito pequenos)
   → Mostra toda a área onde o robô PODE navegar
   → Carregado do campo 'normalPosList'
   → Ajuda a visualizar o layout do espaço

2. LINHAS ROXAS TRACEJADAS
   → Paredes, obstáculos, limites do ambiente
   → Carregado do campo 'lineList'
   → Define os limites físicos

3. CAIXAS LARANJAS COM MARCADORES VERMELHOS
   → Landmarks (pontos de destino)
   → Carregado do campo 'landmarkList'
   → Cada um tem um ID (LM1, LM2, etc.)

4. SETA AZUL
   → O robô em tempo real
   → Aponta para a direção que o robô está olhando
   → Se atualiza conforme o robô se move

5. LINHA VERDE
   → Trajetória percorrida
   → Mostra o caminho que o robô já percorreu
   → Últimos [COMPRIMENTO_TRAJETORIA] pontos

6. ESTRELA VERMELHA
   → Destino atual (quando navegando)
   → Aparece quando o robô está indo para um landmark

7. EIXOS DE REFERÊNCIA
   → Seta vermelha = eixo X
   → Seta verde = eixo Y
   → Origem (0,0) marcada

================================================================================
⚙️  LIMITES AUTOMÁTICOS
================================================================================

Os limites do gráfico são ajustados automaticamente baseado no arquivo .smap:

  X: de -1.61 até 2.76 metros
  Y: de -0.93 até 6.35 metros

Isso garante que TUDO do mapa seja visível!

================================================================================
🔄 ATUALIZAÇÃO EM TEMPO REAL
================================================================================

O visualizador se atualiza a cada [INTERVALO_ATUALIZACAO] ms, mostrando:
- Posição atual do robô
- Orientação (ângulo)
- Velocidade linear e angular
- Destino atual (se navegando)
- Status da tarefa
- Trajetória percorrida

================================================================================
✅ TUDO PRONTO!
================================================================================

Agora o visualizador tem TODAS as informações do mapa:
✓ Landmarks
✓ Paredes/obstáculos
✓ Área navegável
✓ Posição inicial
✓ Limites corretos

E continua mostrando o robô em tempo real!

🎉 Aproveite!

""")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VISUALIZADOR OFFLINE - Mostra apenas o mapa do arquivo .smap
sem conectar ao robô

Uso: python visualizador_offline.py
"""

import sys
# Força modo offline
sys.argv.append('--offline')

# Importa e executa o visualizador em modo offline
from visualizador_auto import VisualizadorRoboAuto

if __name__ == "__main__":
    print("\n" + "="*60)
    print("📴 VISUALIZADOR OFFLINE DO ROBOSHOP PRO")
    print("="*60)
    print("\n✨ Mostrando apenas o mapa do arquivo .smap")
    print("  • Não conecta ao robô")
    print("  • Carrega mapa de: InnovationBox.smap, map.smap ou mapa.smap")
    print("\n")
    
    try:
        visualizador = VisualizadorRoboAuto(modo_offline=True)
        visualizador.iniciar()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()

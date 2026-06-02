from netprotocol.rbkNetProtoEnums import *
import netprotocol.rbkNetProtoEnums
import json
import socket
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np
from collections import deque

# ============ CONFIGURAÇÕES ============
ROBOT_IP = '10.101.251.137'  # Ajuste para o IP do seu robô

# Configurações visuais
TAMANHO_ROBO = 0.5  # metros
COMPRIMENTO_TRAJETORIA = 500  # número de pontos da trajetória
INTERVALO_ATUALIZACAO = 100  # ms

# ============ CLASSE VISUALIZADOR ============

class VisualizadorRobo:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 10))
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlabel('X (metros)', fontsize=12)
        self.ax.set_ylabel('Y (metros)', fontsize=12)
        self.ax.set_title('🤖 VISUALIZAÇÃO DO ROBÔ EM TEMPO REAL', fontsize=14, fontweight='bold')
        
        # Conexões com o robô
        self.so_state = None
        self.so_area = None
        self.conectar()
        
        # Dados do robô
        self.pos_x = 0
        self.pos_y = 0
        self.angulo = 0
        self.velocidade_linear = 0
        self.velocidade_angular = 0
        
        # Trajetória
        self.trajetoria_x = deque(maxlen=COMPRIMENTO_TRAJETORIA)
        self.trajetoria_y = deque(maxlen=COMPRIMENTO_TRAJETORIA)
        
        # Áreas detectadas
        self.areas_detectadas = []
        
        # Landmarks conhecidos (ajuste conforme seu mapa)
        self.landmarks = {
            'LM1': (0, 0),
            'LM2': (5, 0),
            'LM3': (10, 0),
            'LM4': (0, 5),
            'LM5': (5, 5),
            'LM6': (10, 5),
        }
        
        # Elementos gráficos
        self.robo_patch = None
        self.direcao_line = None
        self.trajetoria_line = None
        self.sensor_patches = []
        self.landmark_plots = []
        self.info_text = None
        
        self.inicializar_graficos()
    
    def conectar(self):
        """Conecta ao robô"""
        try:
            print("🔌 Conectando ao robô...")
            
            # Conexão para localização
            self.so_state = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.so_state.connect((ROBOT_IP, API_PORT_STATE))
            self.so_state.settimeout(1.0)
            print(f"  ✅ Conectado à porta STATE ({API_PORT_STATE})")
            
            # Conexão para áreas/sensores
            self.so_area = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.so_area.connect((ROBOT_IP, API_PORT_STATE))
            self.so_area.settimeout(1.0)
            print(f"  ✅ Conectado à porta STATE para áreas")
            
            print("✅ Conexões estabelecidas!\n")
            
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            raise
    
    def inicializar_graficos(self):
        """Inicializa os elementos gráficos"""
        # Robô (triângulo apontando para frente)
        self.robo_patch = patches.FancyArrow(0, 0, TAMANHO_ROBO, 0, 
                                             width=TAMANHO_ROBO*0.8, 
                                             head_width=TAMANHO_ROBO*1.2,
                                             head_length=TAMANHO_ROBO*0.3,
                                             fc='blue', ec='darkblue', 
                                             linewidth=2, zorder=10)
        self.ax.add_patch(self.robo_patch)
        
        # Trajetória
        self.trajetoria_line, = self.ax.plot([], [], 'g-', alpha=0.5, linewidth=2, label='Trajetória')
        
        # Landmarks
        for nome, (x, y) in self.landmarks.items():
            plot = self.ax.plot(x, y, 'ro', markersize=10, label=f'{nome}')[0]
            self.ax.text(x, y+0.3, nome, ha='center', fontsize=9, fontweight='bold')
            self.landmark_plots.append(plot)
        
        # Texto de informações
        self.info_text = self.ax.text(0.02, 0.98, '', transform=self.ax.transAxes,
                                     verticalalignment='top', fontsize=10,
                                     bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Legenda
        self.ax.legend(loc='upper right')
        
        # Ajusta limites iniciais
        self.ax.set_xlim(-5, 15)
        self.ax.set_ylim(-5, 15)
    
    def ler_posicao(self):
        """Lê a posição atual do robô"""
        try:
            self.so_state.send(packMsg(1, robot_status_loc_req, {}))
            data = self.so_state.recv(16)
            
            if len(data) >= 16:
                jsonDataLen = unpackHead(data)[0]
                if jsonDataLen > 0:
                    data = self.so_state.recv(2048)
                    ret = json.loads(data)
                    
                    # Atualiza posição
                    self.pos_x = ret.get('x', self.pos_x)
                    self.pos_y = ret.get('y', self.pos_y)
                    self.angulo = ret.get('angle', self.angulo)
                    
                    return True
        except socket.timeout:
            pass
        except Exception as e:
            print(f"⚠️ Erro ao ler posição: {e}")
        
        return False
    
    def ler_velocidade(self):
        """Lê a velocidade atual do robô"""
        try:
            self.so_state.send(packMsg(2, robot_status_speed_req, {}))
            data = self.so_state.recv(16)
            
            if len(data) >= 16:
                jsonDataLen = unpackHead(data)[0]
                if jsonDataLen > 0:
                    data = self.so_state.recv(2048)
                    ret = json.loads(data)
                    
                    # Calcula velocidade linear
                    vx = ret.get('vx', 0)
                    vy = ret.get('vy', 0)
                    self.velocidade_linear = np.sqrt(vx**2 + vy**2)
                    self.velocidade_angular = ret.get('w', 0)
                    
                    return True
        except socket.timeout:
            pass
        except Exception as e:
            pass
        
        return False
    
    def ler_areas(self):
        """Lê as áreas detectadas pelos sensores"""
        try:
            self.so_area.send(packMsg(3, robot_status_area_req, {}))
            data = self.so_area.recv(16)
            
            if len(data) >= 16:
                jsonDataLen = unpackHead(data)[0]
                if jsonDataLen > 0:
                    data = self.so_area.recv(2048)
                    ret = json.loads(data)
                    
                    self.areas_detectadas = ret.get('area_ids', [])
                    return True
        except socket.timeout:
            pass
        except Exception as e:
            pass
        
        return False
    
    def atualizar_frame(self, frame):
        """Atualiza o frame da animação"""
        # Lê dados do robô
        self.ler_posicao()
        self.ler_velocidade()
        self.ler_areas()
        
        # Adiciona posição à trajetória
        self.trajetoria_x.append(self.pos_x)
        self.trajetoria_y.append(self.pos_y)
        
        # Atualiza trajetória
        if len(self.trajetoria_x) > 0:
            self.trajetoria_line.set_data(list(self.trajetoria_x), list(self.trajetoria_y))
        
        # Atualiza posição do robô (remove patch antigo e cria novo)
        if self.robo_patch in self.ax.patches:
            self.robo_patch.remove()
        
        # Cria triângulo rotacionado
        dx = TAMANHO_ROBO * np.cos(self.angulo)
        dy = TAMANHO_ROBO * np.sin(self.angulo)
        
        self.robo_patch = patches.FancyArrow(
            self.pos_x, self.pos_y, dx, dy,
            width=TAMANHO_ROBO*0.8, 
            head_width=TAMANHO_ROBO*1.2,
            head_length=TAMANHO_ROBO*0.3,
            fc='blue', ec='darkblue', 
            linewidth=2, zorder=10
        )
        self.ax.add_patch(self.robo_patch)
        
        # Remove patches de sensores anteriores
        for patch in self.sensor_patches:
            if patch in self.ax.patches:
                patch.remove()
        self.sensor_patches.clear()
        
        # Desenha áreas detectadas (círculos ao redor do robô)
        if len(self.areas_detectadas) > 0:
            for i, area_id in enumerate(self.areas_detectadas):
                angulo_area = self.angulo + (i - len(self.areas_detectadas)/2) * 0.3
                dist = 1.5  # distância do sensor
                sensor_x = self.pos_x + dist * np.cos(angulo_area)
                sensor_y = self.pos_y + dist * np.sin(angulo_area)
                
                sensor_circle = patches.Circle(
                    (sensor_x, sensor_y), 0.3, 
                    fc='red', ec='darkred', alpha=0.5, zorder=5
                )
                self.ax.add_patch(sensor_circle)
                self.sensor_patches.append(sensor_circle)
        
        # Atualiza texto de informações
        info = f'📍 Posição: ({self.pos_x:.2f}, {self.pos_y:.2f})\n'
        info += f'🧭 Ângulo: {np.degrees(self.angulo):.1f}°\n'
        info += f'⚡ Vel. Linear: {self.velocidade_linear:.2f} m/s\n'
        info += f'🔄 Vel. Angular: {self.velocidade_angular:.2f} rad/s\n'
        info += f'📡 Áreas: {len(self.areas_detectadas)}'
        if len(self.areas_detectadas) > 0:
            info += f' {self.areas_detectadas}'
        
        self.info_text.set_text(info)
        
        # Ajusta limites da visualização para seguir o robô
        margin = 5
        x_min = min(self.pos_x - margin, min(self.trajetoria_x) if self.trajetoria_x else self.pos_x - margin)
        x_max = max(self.pos_x + margin, max(self.trajetoria_x) if self.trajetoria_x else self.pos_x + margin)
        y_min = min(self.pos_y - margin, min(self.trajetoria_y) if self.trajetoria_y else self.pos_y - margin)
        y_max = max(self.pos_y + margin, max(self.trajetoria_y) if self.trajetoria_y else self.pos_y + margin)
        
        # Inclui landmarks nos limites
        for x, y in self.landmarks.values():
            x_min = min(x_min, x - 2)
            x_max = max(x_max, x + 2)
            y_min = min(y_min, y - 2)
            y_max = max(y_max, y + 2)
        
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        
        return [self.robo_patch, self.trajetoria_line, self.info_text] + self.sensor_patches
    
    def iniciar(self):
        """Inicia a visualização"""
        print("\n🎬 Iniciando visualização...")
        print("📌 Feche a janela para sair\n")
        
        ani = FuncAnimation(self.fig, self.atualizar_frame, 
                          interval=INTERVALO_ATUALIZACAO, 
                          blit=True, cache_frame_data=False)
        
        plt.tight_layout()
        plt.show()
        
        # Fecha conexões ao sair
        if self.so_state:
            self.so_state.close()
        if self.so_area:
            self.so_area.close()
        
        print("\n👋 Visualização encerrada")

# ============ MAIN ============

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🤖 VISUALIZADOR DO ROBÔ EM TEMPO REAL")
    print("="*50)
    print("\n📊 Este programa mostra:")
    print("  • Posição e orientação do robô em tempo real")
    print("  • Trajetória percorrida (linha verde)")
    print("  • Landmarks do mapa (pontos vermelhos)")
    print("  • Áreas detectadas pelos sensores (círculos vermelhos)")
    print("  • Velocidade e informações de estado")
    print("\n⚠️  IMPORTANTE: Configure os landmarks no código")
    print("    de acordo com o seu mapa real!")
    print("\n")
    
    try:
        visualizador = VisualizadorRobo()
        visualizador.iniciar()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
